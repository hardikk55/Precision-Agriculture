# Precision Agriculture Digital Farm — V3 Hardware-Ready

This frontend-only university prototype for Prof. Lalit Kumar models a 3 × 3 digital farm. Every digital `(row, column)` patch maps one-to-one to the future physical patch at the same coordinate.

## Implemented now

- V2's complete simulation: 9 patches, 9 mapped simulated capacitive sensors (`S00`–`S22`), controlled noise, bounded history, graph, manual test mode, MANUAL/AUTO irrigation, cooldown, virtual solenoids, dashboard, log, simulation clock, and reset.
- A hardware-ready data-source selector: **Simulation** remains the default; **Hardware** is safe while disconnected and preserves simulation data for switching back.
- A compact hardware status strip with ESP32, sensor, actuator, and 3 × 3 sensor-map status.
- Typed ESP32 sensor and irrigation-command contracts, without a backend, GPIO access, or fabricated production readings.

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

Physical ESP32 networking, pump drivers, relay circuitry, solenoids, and sensor hardware are **not implemented yet**. Hardware mode therefore reports ESP32 disconnected, 0/9 hardware sensors active, and actuator unavailable; it does not crash or erase simulated farm state.

## Actuation architecture

The existing `VirtualSolenoidActuator` remains the active simulation implementation and only updates the commanded patch. A future `ESP32Actuator` can use the typed `IrrigationCommand` contract to invoke physical pump/solenoid hardware through appropriate driver/relay circuitry. The same rule-based decision engine can operate through either path.

## Run locally

```bash
npm install
npm run dev
```

## Production build

```bash
npm run build
```

## Deploy to Vercel

Use build command `npm run build` and output directory `dist`. No backend or environment variables are required for the simulation mode.
