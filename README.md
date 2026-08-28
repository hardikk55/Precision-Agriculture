# Precision Agriculture Digital Farm

A polished, frontend-only MVP for Prof. Lalit Kumar's university Precision Agriculture research project. It models a **3 × 3 digital farm**, with each digital patch mapped one-to-one to a future physical patch at the same `(row, column)` coordinate.

All current values are **simulated prototype data**—not field measurements.

## Current MVP

- Programmatically generated, coordinate-unique 3 × 3 farm state
- Per-patch simulated soil moisture, temperature, humidity, irrigation status, water use, and last irrigation
- Separate simulation clock with start, pause, reset, and 1×/2×/5× speed controls
- Replaceable `RuleBasedDecisionEngine` that flags patches below a configurable moisture threshold
- Coordinate-specific virtual solenoid actuator: `irrigatePatch(row, column)` only changes the requested patch
- Dynamic dashboard, selected-patch inspector, moisture-driven grid, and activity log

## Architecture

`src/models` contains the patch/farm model and central configuration. `src/simulation` supplies simulated sensor changes. `src/decision` contains the replaceable decision-engine interface and rule-based implementation. `src/actuation` holds the virtual solenoid abstraction. `src/state` coordinates those services for React, while `src/components` renders the UI.

This keeps clear future seams for an ESP32 sensor provider, physical solenoid actuator, measured/estimated data, and an ML decision engine—none are implemented in this MVP.

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

Import this repository into Vercel. Use the default Vite build command `npm run build` and output directory `dist`. No backend environment variables are required.
