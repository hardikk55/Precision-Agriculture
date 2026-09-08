import sqlite3
from pathlib import Path


SCHEMA = '''
CREATE TABLE IF NOT EXISTS sensor_readings (
 id INTEGER PRIMARY KEY, timestamp TEXT NOT NULL, node_id TEXT NOT NULL, sensor_id TEXT NOT NULL, row INTEGER NOT NULL, column_number INTEGER NOT NULL,
 raw_adc INTEGER NOT NULL, moisture_percent REAL, temperature REAL, humidity REAL, status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS calibrations (
 id INTEGER PRIMARY KEY, sensor_id TEXT NOT NULL, adc_dry INTEGER NOT NULL, adc_wet INTEGER NOT NULL, version INTEGER NOT NULL, timestamp TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS irrigation_commands (
 id TEXT PRIMARY KEY, created_at TEXT NOT NULL, issued_at TEXT, row INTEGER NOT NULL, column_number INTEGER NOT NULL, valve TEXT NOT NULL,
 requested_volume_ml REAL NOT NULL, duration_ms INTEGER NOT NULL, status TEXT NOT NULL, started_at TEXT, completed_at TEXT,
 moisture_before REAL, moisture_after REAL, error TEXT, retry_count INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS system_state (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS readings_sensor_time ON sensor_readings(sensor_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS commands_status ON irrigation_commands(status, created_at);
'''


def connect(path: str) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True) if Path(path).parent != Path('.') else None
    db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SCHEMA)
    return db
