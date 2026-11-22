# Precision Agriculture Digital Farm — Project Context

## Purpose

University Precision Agriculture project under Prof. Lalit Kumar. V6 has a 2 × 2 physical and digital farm (four patches), with strict one-to-one correspondence:

```
Digital (0,0) ↔ Pot 1   Digital (0,1) ↔ Pot 2
Digital (1,0) ↔ Pot 3   Digital (1,1) ↔ Pot 4
```

## Sensor and environment rules

There are exactly four capacitive soil-moisture sensors—one per physical pot. This mapping is a project invariant:

```
S00 → Pot 1/(0,0)  S01 → Pot 2/(0,1)
S10 → Pot 3/(1,0)  S11 → Pot 4/(1,1)
```

Soil moisture is a 1–5 score, not a percentage. Scores 4/5–5/5 are moist; scores ≤3/5 require irrigation. Preserve original historical scores without percent conversion.

Temperature and humidity are simulated global/environmental measurements. Do not represent them as nine independent physical sensors. The physical sensing priority is the nine moisture sensors.

## Irrigation

Physical target architecture: water tank → pump → manifold → solenoid-controlled irrigation lines → 3 × 3 farm. Coordinate-specific behavior is mandatory: irrigating `(1,2)` must affect only `(1,2)`.

The browser must never directly operate high-power hardware. Future physical control is the ESP32/hardware layer's responsibility, using suitable drivers, relays/MOSFETs, power supplies, reservoir, tubing, and manifold.

## Versions

- **V1:** 3 × 3 grid, nine patches, simulated environment, rule-based irrigation, virtual solenoid, dashboard, inspector, controls, log.
- **V2:** nine simulated capacitive sensors, mapping, controlled noise, periodic sampling, bounded history/graph, manual test, MANUAL/AUTO closed loop and safeguards.
- **V3:** provider/actuator abstractions, Simulation/Hardware concept, ESP32 HTTP contract and hardware status; no real hardware dependency.
- **V4:** monitoring, analytics, timeline, CSV export, and demo scenario (current phase).

## Current architecture

`Sensor Provider → Sensor Reading → Farm/Patch State → RuleBasedDecisionEngine → safety_check → single command queue → ESP32 HTTP polling → sensor feedback`.

Simulation remains runnable independently. V5-Backend adds `server.app`, a compact FastAPI/SQLite backend with server-side calibration, a guarded single-command irrigation queue, HTTP telemetry/acknowledgements, and software E-stop. FastAPI never manipulates GPIO; only the ESP32 executes the fixed hardware sequence. `FARM_ML_PER_SECOND` starts unset, so physical irrigation is blocked until a measured flow rate is configured. MQTT, ML, and cloud infrastructure are not part of this project.

## Scope and development rules

- Preserve working behavior; make incremental changes and avoid unnecessary dependencies.
- Keep simulation runnable with `npm run dev`, independent of hardware.
- Keep provider/actuator abstractions clean; do not put business logic in components.
- Use actual farm state for dashboard/analytics; do not hardcode statistics.
- Keep 2 × 2 and sensor mappings as a single source of truth. V6 seeds its protected historical workbook automatically and keeps historical, live, and simulated readings separate.
- Do not add ML, gantry, robotic arm, fertilizer, pesticide, computer vision, or optimization unless explicitly requested.
- Do not claim real ESP32/hardware operation unless connected and tested.
- Run `npm run build` after significant changes.
- Update this AGENTS.md whenever a major architectural or project decision changes, so future developers/Codex sessions do not depend on chat history.

## Roadmap

V1 basic digital farm → V2 sensor-driven closed-loop simulation → V3 hardware-ready software → V4 monitoring/analytics/demo → V5-Backend backend/ESP32 integration → future ML/prediction/optimization. This roadmap may evolve with professor feedback.
