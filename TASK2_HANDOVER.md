# V6 frontend redesign handover

## Completed

- Added the dedicated Historical Replay workspace with actual timestamp-based playback (1×, 5×, 10×, and 100×), restart, timeline scrubbing, active dataset selection, synchronized four-pot/environment readings, and recorded-event log. `src/state/useHistoricalReplay.ts` precomputes timestamp-grouped snapshots rather than sampling or fabricating readings during playback.
- Historical water flow now uses recorded watering events only. Replay is distinct from interactive simulation, and recorded hardware mode remains static/read-only.
- Added an explicitly labelled, configurable estimated plant-growth model (crop suitability, rate, initial size, and maximum size). It deterministically uses the historical moisture, temperature, and humidity values and scales the replay twin's four plants; it must not be interpreted as observed crop data.
- Added the production 3D irrigation twin with `three`, `@react-three/fiber`, and `@react-three/drei`. It includes a 2×2 pot layout, shared reservoir/12V diaphragm pump/distribution manifold, ESP32 controller, four independent solenoids, four pipes, and visible capacitive sensors. It retains a static fallback when WebGL is unavailable.
- Refined the twin camera into a resettable isometric overview with camera-facing outlined labels, free orbiting, bounded useful zoom, responsive canvas sizing, selected-pot highlighting, and separate pump/valve/water-flow status cues.
- Replaced the analytics sparkline with timestamp-sorted, separate, explicitly non-filled SVG line series. Soil moisture supports S00–S11 visibility toggles and all research charts expose actual sampled values on hover; environmental values are correctly aggregated as global readings by timestamp.
- Rebuilt the visible application shell as the **Precision Agriculture Field Research Console**: persistent forest navigation on desktop, compact mobile navigation, page-specific toolbar, and dedicated Digital Farm, Analytics, Irrigation History, and Dataset Management routes.
- Added `src/components/IrrigationSystem3D.tsx`, a dependency-free, interactive SVG/isometric irrigation-system twin. It represents one reservoir, shared pump and manifold, four valves (V1–V4), four distinct paths, and the Pot 1/S00 through Pot 4/S11 mapping. It follows the existing `Patch.irrigationStatus` state only: a simulated command activates the shared pump, exactly its mapped valve, and only that water path. Recorded mode is intentionally static and labelled as such.
- Redesigned the selected-pot inspector and farm cards to surface Pot/Sensor/coordinate, the 1–5 score, condition, source, and mode-safe controls without suggesting live hardware operation.
- Added a forest/sage/amber design system in `src/redesign.css`, imported by `src/main.tsx`.
- Refined dashboard hierarchy, responsive 2×2 farm cards, status panels, analytics cards, tables, charts, selected-pot inspector, and historical workspace styling.
- Added `src/components/AnalyticsDashboard.tsx`, driven only by the selected backend dataset. It includes sensor/date filters, moisture summary statistics, threshold percentage, per-pot comparisons, environmental summary, trends, and calculated observations.
- Preserved `HistoricalWorkspace` dataset management, imports, irrigation history filters, and CSV exports.
- Preserved separate recorded-hardware and simulation modes. Historical data remains read-only.
- The five-point score convention remains: 4–5 moist; ≤3 irrigation required.

## Key files

- `src/App.tsx` composes the shell, page navigation, data-source selector, and mode-safe content.
- `src/components/IrrigationSystem3D.tsx` is the reusable React Three Fiber twin, with a safe static fallback, and uses the existing simulation state rather than a separate controller.
- `src/redesign.css` contains shared design tokens and responsive layout rules.
- `src/components/AnalyticsDashboard.tsx` is the main Task 2 analytics component.
- Existing data comes from `useHistoricalDataset`, `historicalApi`, and backend `/api/datasets` plus `/api/datasets/{id}/readings`.

## Remaining opportunities

- Charts are intentionally dependency-free SVG sparklines; add a chart library only if interactive hover tooltips/axis detail is required.
- The existing `HistoricalWorkspace` analytics tab remains a compact secondary view; it could be consolidated with `AnalyticsDashboard` in a later navigation redesign.
- Visually inspect the live browser after restarting Vite, especially the dataset API proxy path.

## Verification

- `npm run build` completed successfully after the console and irrigation-twin work.
- `git diff --check` completed with no whitespace errors.
- Browser verification confirmed recorded mode remains static/read-only, simulation of Pot 4 activates only V4 and the shared pump, and the pump/valve return to idle after the existing simulation completes. Recorded analytics rendered all four sensor series and environmental charts for 1,632 readings.
- No backend schema, API contract, historical workbook, or decision-engine changes were made.
- Manual checks recommended: switch datasets, set sensor/date filters, download both CSV exports, view irrigation-history filters, and switch to Simulation mode.

## Design conventions

- Use variables in `redesign.css`: `--forest`, `--sage`, `--amber`, `--paper`, `--line`, and `--radius`.
- Prefer compact grouped statistics over isolated oversized cards.
- Moisture must always be labelled `/5`; humidity retains `%`, temperature `°C`, rainfall `mm`.

## Task 6 — historical environment and presentation mode

- Added `src/environment/solar.ts`: an offline NOAA-style solar approximation that drives background palette, directional sun/moon, ambient light, and night stars from the replay playhead. It gracefully falls back to a clock-phase palette until a farm location is configured.
- Location was deliberately not guessed. No latitude/longitude exists in the documentation, and `server/datasets.py` attaches UTC to imported naïve Excel timestamps. The replay panel therefore requests latitude, longitude, and IANA timezone for calculated sunrise/sunset/elevation, while retaining imported data semantics.
- The 3D twin remains freely orbitable and zoomable; Reset View restores its default isometric composition. Historical water flow continues to show only recorded events and mapped valve paths.
- Added `PresentationMode` with six navigable scenes: introduction, architecture, historical experiment, interactive replay, analytics, and factual summary. Controls support Previous/Next, scene dots, auto-advance, Space, Arrow keys, and Escape/Exit.
- Verification: `npm run build` passed. Browser verification confirmed the replay panel’s configuration state and recorded watering synchronization; configured sample values produced calculated solar readings; all six presentation scenes rendered and navigation returned cleanly to the dashboard.
