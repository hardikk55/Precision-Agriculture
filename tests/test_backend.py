from dataclasses import replace
from datetime import timedelta
from fastapi.testclient import TestClient
import server.app as backend
from server.calibration import moisture_percent
from server.farm_map import BY_PATCH, BY_SENSOR


def client(tmp_path, monkeypatch, flow=10.0):
    monkeypatch.setattr(backend, 'settings', replace(backend.settings, database_path=str(tmp_path / 'test.db'), flow_ml_per_second=flow))
    return TestClient(backend.app)


def telemetry(c, raw=2000):
    return c.post('/api/telemetry', json={'node_id': 'esp32-farm-01', 'readings': [{'sensor_id': f'S{r}{col}', 'raw_adc': raw} for r in range(3) for col in range(3)]})


def calibrate(c):
    for sensor in BY_SENSOR: assert c.put(f'/api/calibrations/{sensor}', json={'adc_dry': 3000, 'adc_wet': 1000}).status_code == 200


def test_mapping_and_calibration_bounds():
    assert len(BY_SENSOR) == len(BY_PATCH) == 9
    assert BY_PATCH[(0, 0)].sensor_id == 'S00' and BY_PATCH[(2, 2)].valve == 'V9'
    assert moisture_percent(3000, 3000, 1000) == 0
    assert moisture_percent(1000, 3000, 1000) == 100
    assert moisture_percent(500, 1000, 3000) == 0 and moisture_percent(4000, 1000, 3000) == 100


def test_telemetry_sensors_and_safe_irrigation(tmp_path, monkeypatch):
    with client(tmp_path, monkeypatch) as c:
        assert c.get('/api/health').status_code == 200
        assert len(c.get('/api/sensors').json()['sensors']) == 9
        calibrate(c); response = telemetry(c, 2000); assert response.status_code == 201
        record = c.get('/api/sensors').json()['sensors'][0]
        assert record['raw_adc'] == 2000 and record['moisture_percent'] == 50
        command = c.post('/api/actuators/irrigate', json={'patch': {'row': 0, 'column': 0}, 'requestedVolumeMl': 250})
        assert command.status_code == 202 and command.json()['duration_ms'] == 25000
        assert c.post('/api/actuators/irrigate', json={'patch': {'row': 0, 'column': 1}}).status_code == 409
        claimed = c.get('/api/commands').json()['command']; assert claimed['valve'] == 'V1'
        assert c.get('/api/commands').json()['command'] is None
        assert c.post('/api/ack', json={'command_id': claimed['command_id'], 'status': 'started'}).status_code == 200
        assert c.post('/api/ack', json={'command_id': claimed['command_id'], 'status': 'done'}).status_code == 200
        assert c.post('/api/ack', json={'command_id': claimed['command_id'], 'status': 'done'}).status_code == 409


def test_invalid_adc_unset_flow_and_estop(tmp_path, monkeypatch):
    with client(tmp_path, monkeypatch, flow=None) as c:
        calibrate(c)
        assert telemetry(c, 30).json()['readings'][0]['status'] == 'invalid_low'
        assert c.post('/api/actuators/irrigate', json={'patch': {'row': 0, 'column': 0}}).status_code == 422


def test_telemetry_rejects_unknown_sensors_and_invalid_adc_is_persisted(tmp_path, monkeypatch):
    with client(tmp_path, monkeypatch) as c:
        assert c.post('/api/telemetry', json={'node_id': 'esp32-farm-01', 'readings': [{'sensor_id': 'BAD', 'raw_adc': 1000}]}).status_code == 422
        calibrate(c); telemetry(c, 4060)
        sensor = c.get('/api/sensors').json()['sensors'][0]
        assert sensor['raw_adc'] == 4060 and sensor['status'] == 'invalid_high' and sensor['moisture'] is None


def test_duration_limit_staleness_cooldown_daily_cap_and_estop(tmp_path, monkeypatch):
    with client(tmp_path, monkeypatch) as c:
        calibrate(c); telemetry(c)
        assert c.post('/api/actuators/irrigate', json={'patch': {'row': 0, 'column': 0}, 'requestedVolumeMl': 301}).status_code == 409
        database = backend.app.state.db
        database.execute("UPDATE sensor_readings SET timestamp=? WHERE sensor_id='S00'", ((backend.utcnow() - timedelta(seconds=901)).isoformat(),))
        assert c.post('/api/actuators/irrigate', json={'patch': {'row': 0, 'column': 0}}).status_code == 409
        database.execute("UPDATE sensor_readings SET timestamp=? WHERE sensor_id='S00'", (backend.iso_now(),))
        database.execute("INSERT INTO irrigation_commands(id,created_at,row,column_number,valve,requested_volume_ml,duration_ms,status,completed_at) VALUES ('daily',?,?,?,?,?,?,?,?)", (backend.iso_now(),0,0,'V1',5000,1000,'done',backend.iso_now()))
        assert c.post('/api/actuators/irrigate', json={'patch': {'row': 0, 'column': 0}}).status_code == 409
        assert c.post('/api/estop').status_code == 200
        assert c.post('/api/estop/reset').json()['estop'] is False


def test_ack_failed_and_exports(tmp_path, monkeypatch):
    with client(tmp_path, monkeypatch) as c:
        calibrate(c); telemetry(c)
        command = c.post('/api/actuators/irrigate', json={'patch': {'row': 1, 'column': 1}}).json()['command_id']
        assert c.get('/api/commands').json()['command']['command_id'] == command
        assert c.post('/api/ack', json={'command_id': command, 'status': 'started'}).status_code == 200
        assert c.post('/api/ack', json={'command_id': command, 'status': 'failed', 'error': 'pump fault'}).status_code == 200
        assert c.get('/api/commands/history').json()['commands'][0]['status'] == 'failed'
        assert 'raw_adc' in c.get('/api/export.csv?kind=readings').text
        assert 'command_id' in c.get('/api/export.csv?kind=commands').text
        assert c.post('/api/estop').status_code == 200
        assert c.post('/api/actuators/irrigate', json={'patch': {'row': 0, 'column': 0}}).status_code == 409
