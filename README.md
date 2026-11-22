# Precision Agriculture Digital Farm — V6 2×2 Data Integration

V6 represents exactly four physical pots: Pot 1/S00 `(0,0)`, Pot 2/S01 `(0,1)`, Pot 3/S10 `(1,0)`, and Pot 4/S11 `(1,1)`. GPIO, ADC/MUX and wiring identifiers are intentionally not guessed; the ESP32 firmware remains their authority.

## Soil-moisture scale

Historical soil moisture is a **1–5 score**, not a percentage. Scores **4/5 and 5/5** are sufficiently moist; **3/5, 2/5, and 1/5** require irrigation. The inclusive irrigation threshold is **≤3/5**. The original workbook values are stored unchanged and exports label these fields `soil_moisture_score_out_of_5`.

## Historical data and datasets

The supplied source workbook is preserved at `data/soil_moisture_weather_log_with_watering_status.xlsx`. On backend startup it is automatically and transactionally imported once as a protected seed dataset. The mapper uses Check date + Check time, Pot, raw ADC, before/after moisture, Watering status, temperature, humidity and rain fields. It maps `Pot 1`–`Pot 4` to the four V6 sensors and stores source metadata separately from live telemetry.

Dataset endpoints provide `GET /api/datasets`, `POST /api/datasets/preview?filename=...`, `POST /api/datasets/import?filename=...`, `PUT /api/datasets/{id}/active`, `GET /api/datasets/{id}/readings`, and protected deletion. Upload raw CSV (or compatible XLSX) bytes after preview. Files are validated for timestamps, numeric moisture, all four pots, duplicate timestamp/sensor pairs, and unsupported identifiers. Historical imports never issue irrigation commands.

## Optional ESP32 connectivity

The browser uses `VITE_FARM_API_URL` (default `http://localhost:8000`) and calls FastAPI, not GPIO. `/api/health` and `/api/connection/status` report backend/recent telemetry state. Firmware must POST four unique sensor IDs (`S00`, `S01`, `S10`, `S11`) to `/api/telemetry`; it polls `/api/commands` and acknowledges `/api/ack`. Live connectivity has not been physically tested. Historical data remains usable offline. `FARM_ML_PER_SECOND` must be measured and configured before physical irrigation can be queued.

This project combines the V4 React dashboard with a FastAPI/SQLite backend. Every digital `(row, column)` patch maps one-to-one to the physical patch at the same coordinate.

## Implemented now

- V2's complete simulation: 9 patches, 9 mapped simulated capacitive sensors (`S00`–`S22`), controlled noise, bounded history, graph, manual test mode, MANUAL/AUTO irrigation, cooldown, virtual solenoids, dashboard, log, simulation clock, and reset.
- A hardware-ready data-source selector: **Simulation** remains the default; **Hardware** is safe while disconnected and preserves simulation data for switching back.
- A compact hardware status strip with ESP32, sensor, actuator, and 3 × 3 sensor-map status.
- Typed ESP32 sensor and irrigation-command contracts, without a backend, GPIO access, or fabricated production readings.
- V4 monitoring: sensor health/age analytics, bounded chronological event timeline, browser CSV exports, and a closed-loop demo scenario.

## Sensor architecture

The single source of truth creates exactly nine sensor mappings: `S00`–`S02`, `S10`–`S12`, and `S20`–`S22`, each at its matching patch coordinate. The simulation uses `SimulatedCapacitiveMoistureSensorProvider`; the future boundary is `ESP32SensorProvider`. Both are isolated from React components and the rule-based decision engine.

## ESP32 HTTP contract (future integration)

The future ESP32 service should expose `GET /api/sensors`:

```json
{ "sensors": [{ "id": "S00", "row": 0, "column": 0, "moisture": 42, "timestamp": "2026-08-29T08:00:00Z", "status": "active" }] }
```

For logical irrigation, the browser-side adapter defines a future `POST /api/actuators/irrigate` command:

```json
{ "patch": { "row": 1, "column": 2 }, "action": "IRRIGATE", "durationMs": 650 }
```

The browser uses `VITE_FARM_API_URL` (default `http://localhost:8000`) for the backend sensor boundary. FastAPI never controls GPIO; the ESP32 polls `/api/commands` and executes the fixed valve/pump sequence.

## Actuation architecture

The existing `VirtualSolenoidActuator` remains the active simulation implementation and only updates the commanded patch. A future `ESP32Actuator` can use the typed `IrrigationCommand` contract to invoke physical pump/solenoid hardware through appropriate driver/relay circuitry. The same rule-based decision engine can operate through either path.

## Run locally

```bash
npm install
npm run dev
```

In a second terminal, start the backend:

```bash
python -m venv .venv
.venv\\Scripts\\python -m pip install -r requirements.txt
.venv\\Scripts\\python -m uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

`FARM_ML_PER_SECOND` is deliberately unset by default. Set it only after measuring the physical flow rate; irrigation remains safely disabled until then.

## Production build

```bash
npm run build
```

## Deploy to Vercel

Use build command `npm run build` and output directory `dist`. No backend or environment variables are required for the simulation mode.
