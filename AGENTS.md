# Precision Agriculture Digital Farm — Project Context

## Purpose

University Precision Agriculture project under Prof. Lalit Kumar. The goal is a small digital twin that will later connect to a physical prototype. The physical and digital farms are both 3 × 3 (9 patches), with strict one-to-one correspondence:

```
Digital (0,0) ↔ Physical (0,0)   Digital (0,1) ↔ Physical (0,1)   Digital (0,2) ↔ Physical (0,2)
Digital (1,0) ↔ Physical (1,0)   Digital (1,1) ↔ Physical (1,1)   Digital (1,2) ↔ Physical (1,2)
Digital (2,0) ↔ Physical (2,0)   Digital (2,1) ↔ Physical (2,1)   Digital (2,2) ↔ Physical (2,2)
```

## Sensor and environment rules

There are exactly nine capacitive soil-moisture sensors—one per physical patch. This mapping is a project invariant and must not change without explicit project approval:

```
S00 → (0,0)  S01 → (0,1)  S02 → (0,2)
S10 → (1,0)  S11 → (1,1)  S12 → (1,2)
S20 → (2,0)  S21 → (2,1)  S22 → (2,2)
```

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

`Sensor Provider → Sensor Reading → Farm/Patch State → RuleBasedDecisionEngine → Actuator Provider → Irrigation → updated moisture → sensor feedback`.

Simulation is the working implementation. `SimulatedCapacitiveMoistureSensorProvider`, `SimulatedEnvironmentProvider`, and `VirtualSolenoidActuator` live separately from React UI. `ESP32HttpSensorProvider` is a typed, disconnected-safe boundary for future HTTP integration. React/Vite/TypeScript are the project technologies; no backend, database, MQTT, or authentication exists.

## Scope and development rules

- Preserve working behavior; make incremental changes and avoid unnecessary dependencies.
- Keep simulation runnable with `npm run dev`, independent of hardware.
- Keep provider/actuator abstractions clean; do not put business logic in components.
- Use actual farm state for dashboard/analytics; do not hardcode statistics.
- Keep 3 × 3 and sensor mappings as a single source of truth.
- Do not add ML, gantry, robotic arm, fertilizer, pesticide, computer vision, or optimization unless explicitly requested.
- Do not claim real ESP32/hardware operation unless connected and tested.
- Run `npm run build` after significant changes.
- Update this AGENTS.md whenever a major architectural or project decision changes, so future developers/Codex sessions do not depend on chat history.

## Roadmap

V1 basic digital farm → V2 sensor-driven closed-loop simulation → V3 hardware-ready software → V4 monitoring/analytics/demo → V5 ESP32/software integration → V6 physical hardware integration → future ML/prediction/optimization. This roadmap may evolve with professor feedback.
