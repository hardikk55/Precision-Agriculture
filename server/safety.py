from datetime import datetime, timedelta, timezone
from .config import MAX_DURATION_MS


class SafetyError(ValueError): pass


def utcnow() -> datetime: return datetime.now(timezone.utc)
def parse_time(value: str) -> datetime: return datetime.fromisoformat(value.replace("Z", "+00:00"))


def safety_check(db, mapping, volume_ml: float, duration_ms: int, flow_ml_per_second: float | None, sensor_max_age_seconds: int, cooldown_minutes: int, daily_volume_cap_ml: float) -> None:
    if flow_ml_per_second is None or flow_ml_per_second <= 0: raise SafetyError("Measured ML_PER_SECOND is not configured")
    if volume_ml <= 0: raise SafetyError("Requested volume must be positive")
    if duration_ms <= 0 or duration_ms > MAX_DURATION_MS: raise SafetyError("Calculated duration is outside the safe limit")
    if db.execute("SELECT 1 FROM irrigation_commands WHERE status IN ('pending','claimed','started')").fetchone(): raise SafetyError("An irrigation command is already pending or active")
    if db.execute("SELECT value FROM system_state WHERE key='estop' AND value='1'").fetchone(): raise SafetyError("Emergency stop is engaged")
    latest = db.execute("SELECT * FROM sensor_readings WHERE sensor_id=? ORDER BY timestamp DESC LIMIT 1", (mapping.sensor_id,)).fetchone()
    if not latest or latest['status'] != 'valid' or latest['moisture_percent'] is None: raise SafetyError("A valid calibrated sensor reading is required")
    if utcnow() - parse_time(latest['timestamp']) > timedelta(seconds=sensor_max_age_seconds): raise SafetyError("Sensor reading is stale")
    cooldown = db.execute("SELECT completed_at FROM irrigation_commands WHERE row=? AND column_number=? AND status='done' ORDER BY completed_at DESC LIMIT 1", (mapping.row, mapping.column)).fetchone()
    if cooldown and utcnow() - parse_time(cooldown['completed_at']) < timedelta(minutes=cooldown_minutes): raise SafetyError("Patch irrigation cooldown is active")
    today = utcnow().date().isoformat()
    delivered = db.execute("SELECT COALESCE(SUM(requested_volume_ml), 0) FROM irrigation_commands WHERE row=? AND column_number=? AND status='done' AND completed_at >= ?", (mapping.row, mapping.column, today)).fetchone()[0]
    if delivered + volume_ml > daily_volume_cap_ml: raise SafetyError("Daily volume cap would be exceeded")
