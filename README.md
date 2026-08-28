# Precision Agriculture Digital Farm — V2

A frontend-only university prototype for Prof. Lalit Kumar's Precision Agriculture project. The 3 × 3 digital farm maps one-to-one to a future 3 × 3 physical farm: each `(row, column)` digital patch represents the physical patch at the same coordinate.

All current sensor values are simulated prototype data, not field measurements.

## V2: closed-loop sensor prototype

- Nine simulated capacitive soil-moisture sensors, `S00` through `S22`, mapped one-to-one to nine patches
- Sensor readings are derived from underlying patch moisture with small, configurable measurement noise
- Global simulated environmental temperature and humidity; no fake per-patch environmental sensors
- Bounded per-patch moisture history (160 readings) and a lightweight selected-patch moisture graph
- Manual sensor test control, constrained to 0–100%
- MANUAL / AUTO irrigation modes; AUTO targets only dry, idle patches and honors a configurable cooldown
- Coordinate-specific virtual solenoid irrigation, water-use accounting, dashboard, activity log, simulation clock, speeds, pause, and reset

## Architecture

`src/models` holds patch, sensor, history, and configuration types. `src/simulation` contains `SimulatedEnvironmentProvider` and the replaceable `SensorProvider` interface/`SimulatedCapacitiveMoistureSensorProvider` implementation. The sensor provider samples patch moisture and records history. `src/decision` contains the rule-based irrigation engine, while `src/actuation` contains the replaceable virtual solenoid actuator. `src/state` coordinates the Sensor → Digital Twin → Decision → Actuation → Sensor Feedback loop.

Future integration seams are ready for an ESP32 sensor provider, physical solenoid actuator, measured/estimated data, and a future ML decision engine. None of those are implemented here.

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

Import the repository into Vercel with build command `npm run build` and output directory `dist`. No backend or environment variables are required.
