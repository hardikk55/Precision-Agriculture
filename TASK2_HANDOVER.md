# V6 frontend redesign handover

## Completed

- Added a forest/sage/amber design system in `src/redesign.css`, imported by `src/main.tsx`.
- Refined dashboard hierarchy, responsive 2×2 farm cards, status panels, analytics cards, tables, charts, selected-pot inspector, and historical workspace styling.
- Added `src/components/AnalyticsDashboard.tsx`, driven only by the selected backend dataset. It includes sensor/date filters, moisture summary statistics, threshold percentage, per-pot comparisons, environmental summary, trends, and calculated observations.
- Preserved `HistoricalWorkspace` dataset management, imports, irrigation history filters, and CSV exports.
- Preserved separate recorded-hardware and simulation modes. Historical data remains read-only.
- The five-point score convention remains: 4–5 moist; ≤3 irrigation required.

## Key files

- `src/App.tsx` composes the redesigned dashboard and analytics.
- `src/redesign.css` contains shared design tokens and responsive layout rules.
- `src/components/AnalyticsDashboard.tsx` is the main Task 2 analytics component.
- Existing data comes from `useHistoricalDataset`, `historicalApi`, and backend `/api/datasets` plus `/api/datasets/{id}/readings`.

## Remaining opportunities

- Charts are intentionally dependency-free SVG sparklines; add a chart library only if interactive hover tooltips/axis detail is required.
- The existing `HistoricalWorkspace` analytics tab remains a compact secondary view; it could be consolidated with `AnalyticsDashboard` in a later navigation redesign.
- Visually inspect the live browser after restarting Vite, especially the dataset API proxy path.

## Verification

- Run `npm run build` after frontend changes. No backend schema/API changes were made for the redesign.
- Manual checks recommended: switch datasets, set sensor/date filters, download both CSV exports, view irrigation-history filters, and switch to Simulation mode.

## Design conventions

- Use variables in `redesign.css`: `--forest`, `--sage`, `--amber`, `--paper`, `--line`, and `--radius`.
- Prefer compact grouped statistics over isolated oversized cards.
- Moisture must always be labelled `/5`; humidity retains `%`, temperature `°C`, rainfall `mm`.
