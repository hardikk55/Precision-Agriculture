import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_path: str = os.getenv("FARM_DATABASE_PATH", "farm.db")
    allowed_origins: tuple[str, ...] = tuple(filter(None, os.getenv("FARM_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")))
    flow_ml_per_second: float | None = float(os.environ["FARM_ML_PER_SECOND"]) if os.getenv("FARM_ML_PER_SECOND") else None
    moisture_threshold_percent: float = float(os.getenv("FARM_MOISTURE_THRESHOLD_PERCENT", "30"))
    cooldown_minutes: int = int(os.getenv("FARM_COOLDOWN_MINUTES", "20"))
    sensor_max_age_seconds: int = int(os.getenv("FARM_SENSOR_MAX_AGE_SECONDS", "900"))
    daily_volume_cap_ml: float = float(os.getenv("FARM_DAILY_VOLUME_CAP_ML", "5000"))


DEFAULT_VOLUME_ML = 250.0
MAX_DURATION_MS = 30_000
ADC_MIN_VALID = 30
ADC_MAX_VALID = 4060
MAX_RETRIES = 2
ACK_TIMEOUT_SECONDS = 60
NODE_ID = "esp32-farm-01"
settings = Settings()
