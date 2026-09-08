# Precision Agriculture Digital Farm — V5-Hardware

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
