import csv
import io
import sqlite3
import threading
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, model_validator

from .calibration import moisture_percent
from .config import ACK_TIMEOUT_SECONDS, ADC_MAX_VALID, ADC_MIN_VALID, DEFAULT_VOLUME_ML, MAX_DURATION_MS, NODE_ID, settings
from .db import connect
from .farm_map import BY_PATCH, BY_SENSOR, PATCHES
from .safety import SafetyError, safety_check, utcnow


def iso_now() -> str: return utcnow().isoformat()

class PatchInput(BaseModel): row: int = Field(ge=0, le=2); column: int = Field(ge=0, le=2)
class TelemetryReading(BaseModel): sensor_id: str; raw_adc: int = Field(ge=0, le=4095)
class Telemetry(BaseModel):
    node_id: str; firmware: str | None = None; readings: list[TelemetryReading] = Field(min_length=1, max_length=9)
    temperature: float | None = None; humidity: float | None = Field(default=None, ge=0, le=100)
    @model_validator(mode='after')
    def unique_sensors(self):
        if len({item.sensor_id for item in self.readings}) != len(self.readings): raise ValueError('Duplicate sensor IDs are not allowed')
        return self
class CalibrationInput(BaseModel): adc_dry: int = Field(ge=0, le=4095); adc_wet: int = Field(ge=0, le=4095)
    
class IrrigationInput(BaseModel):
    patch: PatchInput; requested_volume_ml: float = Field(default=DEFAULT_VOLUME_ML, alias='requestedVolumeMl', gt=0)
    action: Literal['IRRIGATE'] = 'IRRIGATE'
    model_config = {'populate_by_name': True}
class AckInput(BaseModel): command_id: str; status: Literal['started', 'done', 'failed']; error: str | None = Field(default=None, max_length=500)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = connect(settings.database_path); app.state.lock = threading.Lock()
    # A process restart must never assume a valve is still active.
    app.state.db.execute("UPDATE irrigation_commands SET status='failed', completed_at=?, error='Backend restarted before completion' WHERE status IN ('claimed','started')", (iso_now(),))
    yield
    app.state.db.close()

app = FastAPI(title='Digital Farm V5-Hardware Backend', version='0.1.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=list(settings.allowed_origins), allow_credentials=False, allow_methods=['GET','POST','PUT'], allow_headers=['Content-Type'])

def db(request: Request): return request.app.state.db
def fail(message: str, code: int = 422): raise HTTPException(status_code=code, detail=message)
def expire_started(connection):
    cutoff = (utcnow().timestamp() - ACK_TIMEOUT_SECONDS)
    for command in connection.execute("SELECT id, started_at FROM irrigation_commands WHERE status='started'").fetchall():
        if datetime.fromisoformat(command['started_at'].replace('Z','+00:00')).timestamp() < cutoff:
            connection.execute("UPDATE irrigation_commands SET status='failed', completed_at=?, error='ACK timeout' WHERE id=?", (iso_now(), command['id']))

@app.get('/api/health')
def health(request: Request):
    db(request).execute('SELECT 1').fetchone()
    return {'status': 'ok', 'database': 'accessible'}

@app.post('/api/telemetry', status_code=201)
def ingest_telemetry(payload: Telemetry, request: Request):
    if payload.node_id != NODE_ID: fail('Unknown node_id')
    if any(item.sensor_id not in BY_SENSOR for item in payload.readings): fail('Unknown sensor ID')
    connection = db(request); now = iso_now(); accepted = []
    with request.app.state.lock:
        connection.execute('BEGIN IMMEDIATE')
        try:
            for item in payload.readings:
                mapping = BY_SENSOR[item.sensor_id]
                calibration = connection.execute('SELECT * FROM calibrations WHERE sensor_id=? ORDER BY version DESC LIMIT 1', (item.sensor_id,)).fetchone()
                status, calibrated = 'valid', None
                if item.raw_adc <= ADC_MIN_VALID: status = 'invalid_low'
                elif item.raw_adc >= ADC_MAX_VALID: status = 'invalid_high'
                elif calibration:
                    calibrated = moisture_percent(item.raw_adc, calibration['adc_dry'], calibration['adc_wet'])
                else: status = 'uncalibrated'
                connection.execute('INSERT INTO sensor_readings(timestamp,node_id,sensor_id,row,column_number,raw_adc,moisture_percent,temperature,humidity,status) VALUES (?,?,?,?,?,?,?,?,?,?)', (now,payload.node_id,item.sensor_id,mapping.row,mapping.column,item.raw_adc,calibrated,payload.temperature,payload.humidity,status))
                accepted.append({'sensor_id': item.sensor_id, 'status': status, 'moisture_percent': calibrated})
            connection.execute('COMMIT')
        except Exception:
            connection.execute('ROLLBACK'); raise
    return {'timestamp': now, 'readings': accepted}

@app.get('/api/sensors')
def sensors(request: Request):
    connection = db(request); rows = []
    for item in PATCHES:
        reading = connection.execute('SELECT * FROM sensor_readings WHERE sensor_id=? ORDER BY timestamp DESC LIMIT 1', (item.sensor_id,)).fetchone()
        state = 'offline'
        if reading:
            state = reading['status']
            if reading['status'] == 'valid' and (utcnow() - datetime.fromisoformat(reading['timestamp'])).total_seconds() > settings.sensor_max_age_seconds: state = 'stale'
        rows.append({'id': item.sensor_id, 'sensor_id': item.sensor_id, 'row': item.row, 'column': item.column, 'patch': {'row': item.row, 'column': item.column}, 'valve': item.valve, 'raw_adc': reading['raw_adc'] if reading else None, 'moisture': reading['moisture_percent'] if reading else None, 'moisture_percent': reading['moisture_percent'] if reading else None, 'timestamp': reading['timestamp'] if reading else None, 'temperature': reading['temperature'] if reading else None, 'humidity': reading['humidity'] if reading else None, 'status': state})
    return {'sensors': rows}

@app.get('/api/calibrations')
def calibrations(request: Request):
    connection = db(request)
    return {'calibrations': [dict(row) for row in connection.execute('SELECT c.* FROM calibrations c JOIN (SELECT sensor_id, MAX(version) version FROM calibrations GROUP BY sensor_id) latest ON c.sensor_id=latest.sensor_id AND c.version=latest.version')]}

@app.get('/api/calibrations/{sensor_id}/history')
def calibration_history(sensor_id: str, request: Request):
    if sensor_id not in BY_SENSOR: fail('Unknown sensor ID', 404)
    return {'calibrations': [dict(row) for row in db(request).execute('SELECT * FROM calibrations WHERE sensor_id=? ORDER BY version DESC', (sensor_id,))]}

@app.put('/api/calibrations/{sensor_id}')
def set_calibration(sensor_id: str, payload: CalibrationInput, request: Request):
    if sensor_id not in BY_SENSOR: fail('Unknown sensor ID', 404)
    if payload.adc_dry == payload.adc_wet: fail('ADC_DRY and ADC_WET must differ')
    connection = db(request); version = connection.execute('SELECT COALESCE(MAX(version),0)+1 FROM calibrations WHERE sensor_id=?', (sensor_id,)).fetchone()[0]
    row = {'sensor_id': sensor_id, 'adc_dry': payload.adc_dry, 'adc_wet': payload.adc_wet, 'version': version, 'timestamp': iso_now()}
    connection.execute('INSERT INTO calibrations(sensor_id,adc_dry,adc_wet,version,timestamp) VALUES (:sensor_id,:adc_dry,:adc_wet,:version,:timestamp)', row)
    return row

@app.post('/api/actuators/irrigate', status_code=202)
def irrigate(payload: IrrigationInput, request: Request):
    mapping = BY_PATCH.get((payload.patch.row, payload.patch.column))
    if not mapping: fail('Unknown patch')
    if settings.flow_ml_per_second is None: fail('Measured ML_PER_SECOND is not configured; physical irrigation is disabled')
    duration = round(payload.requested_volume_ml / settings.flow_ml_per_second * 1000)
    connection = db(request)
    try:
        with request.app.state.lock:
            expire_started(connection)
            safety_check(connection, mapping, payload.requested_volume_ml, duration, settings.flow_ml_per_second, settings.sensor_max_age_seconds, settings.cooldown_minutes, settings.daily_volume_cap_ml)
            latest = connection.execute('SELECT moisture_percent FROM sensor_readings WHERE sensor_id=? ORDER BY timestamp DESC LIMIT 1', (mapping.sensor_id,)).fetchone()
            command = {'id': str(uuid.uuid4()), 'created_at': iso_now(), 'row': mapping.row, 'column_number': mapping.column, 'valve': mapping.valve, 'requested_volume_ml': payload.requested_volume_ml, 'duration_ms': duration, 'status': 'pending', 'moisture_before': latest['moisture_percent']}
            connection.execute('INSERT INTO irrigation_commands(id,created_at,row,column_number,valve,requested_volume_ml,duration_ms,status,moisture_before) VALUES (:id,:created_at,:row,:column_number,:valve,:requested_volume_ml,:duration_ms,:status,:moisture_before)', command)
    except SafetyError as error: fail(str(error), 409)
    return {'command_id': command['id'], 'patch': payload.patch.model_dump(), 'valve': mapping.valve, 'duration_ms': duration, 'status': 'pending'}

@app.get('/api/commands')
def claim_command(request: Request):
    connection = db(request)
    with request.app.state.lock:
        expire_started(connection); connection.execute('BEGIN IMMEDIATE')
        try:
            command = connection.execute("SELECT * FROM irrigation_commands WHERE status='pending' ORDER BY created_at LIMIT 1").fetchone()
            if command: connection.execute("UPDATE irrigation_commands SET status='claimed', issued_at=? WHERE id=? AND status='pending'", (iso_now(), command['id']))
            connection.execute('COMMIT')
        except Exception: connection.execute('ROLLBACK'); raise
    if not command: return {'command': None}
    return {'command': {'command_id': command['id'], 'valve': command['valve'], 'patch': {'row': command['row'], 'column': command['column_number']}, 'duration_ms': command['duration_ms'], 'requested_volume_ml': command['requested_volume_ml'], 'sequence': {'valve_open_delay_ms': 300, 'pump_run_ms': command['duration_ms'], 'pump_stop_delay_ms': 300}}}

@app.post('/api/ack')
def ack(payload: AckInput, request: Request):
    connection = db(request)
    with request.app.state.lock:
        expire_started(connection); command = connection.execute('SELECT * FROM irrigation_commands WHERE id=?', (payload.command_id,)).fetchone()
        if not command: fail('Unknown command', 404)
        if payload.status == 'started' and command['status'] == 'claimed': connection.execute("UPDATE irrigation_commands SET status='started', started_at=? WHERE id=?", (iso_now(), payload.command_id))
        elif payload.status in ('done','failed') and command['status'] == 'started':
            after = connection.execute('SELECT moisture_percent FROM sensor_readings WHERE row=? AND column_number=? AND status=\'valid\' ORDER BY timestamp DESC LIMIT 1', (command['row'], command['column_number'])).fetchone()
            connection.execute('UPDATE irrigation_commands SET status=?, completed_at=?, error=?, moisture_after=? WHERE id=?', (payload.status, iso_now(), payload.error if payload.status == 'failed' else None, after['moisture_percent'] if after else None, payload.command_id))
        else: fail('Invalid or replayed command state transition', 409)
    return {'command_id': payload.command_id, 'status': payload.status}

@app.post('/api/estop')
def estop(request: Request):
    connection = db(request)
    with request.app.state.lock:
        connection.execute("INSERT INTO system_state(key,value) VALUES ('estop','1') ON CONFLICT(key) DO UPDATE SET value='1'")
        connection.execute("UPDATE irrigation_commands SET status='cancelled', completed_at=?, error='Software emergency stop engaged' WHERE status IN ('pending','claimed')", (iso_now(),))
    return {'estop': True, 'note': 'Software interlock engaged; the physical master switch remains the electrical cutoff.'}

@app.post('/api/estop/reset')
def reset_estop(request: Request):
    db(request).execute("INSERT INTO system_state(key,value) VALUES ('estop','0') ON CONFLICT(key) DO UPDATE SET value='0'")
    return {'estop': False}

@app.get('/api/commands/history')
def command_history(request: Request): return {'commands': [dict(item) for item in db(request).execute('SELECT * FROM irrigation_commands ORDER BY created_at DESC LIMIT 200')]}

@app.get('/api/export.csv')
def export_csv(request: Request, kind: Literal['readings', 'commands'] = 'readings'):
    output = io.StringIO(); writer = csv.writer(output)
    if kind == 'readings':
        writer.writerow(['timestamp','node_id','sensor_id','row','column','raw_adc','moisture_percent','temperature','humidity','status'])
        writer.writerows(tuple(row) for row in db(request).execute('SELECT timestamp,node_id,sensor_id,row,column_number,raw_adc,moisture_percent,temperature,humidity,status FROM sensor_readings ORDER BY timestamp'))
        filename = 'farm-readings.csv'
    else:
        writer.writerow(['command_id','created_at','row','column','valve','requested_volume_ml','duration_ms','status','started_at','completed_at','error'])
        writer.writerows(tuple(row) for row in db(request).execute('SELECT id,created_at,row,column_number,valve,requested_volume_ml,duration_ms,status,started_at,completed_at,error FROM irrigation_commands ORDER BY created_at'))
        filename = 'farm-irrigation-history.csv'
    return StreamingResponse(iter([output.getvalue()]), media_type='text/csv', headers={'Content-Disposition': f'attachment; filename={filename}'})
