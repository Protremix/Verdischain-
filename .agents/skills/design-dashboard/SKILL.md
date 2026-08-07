# design-dashboard

## When to Use
When the user requests a dashboard (blockchain stats, platform metrics, monitoring).

## Workflow

1. **Clarify** — Ask (if not provided):
   - Which project: `verdis` or `evolvixos`?
   - What data sources/metrics to display?
   - Real-time (WebSocket) or static?

2. **Select Theme** — Load project's default theme via `getTheme`

3. **Generate** — Use `anthropics--interactive-dashboard-builder` skill:
   - Chart.js for visualizations (line, bar, doughnut, area)
   - Dropdown filters for time ranges, categories
   - Stat cards for KPIs (large gradient numbers, uppercase labels)
   - Data tables with monospace numerics, hover highlight

4. **Layout Pattern**
   - Top: navbar with brand + nav links + status indicator
   - Stats grid: 4-6 stat cards in a responsive grid
   - Charts: 2-column grid (1-column on mobile)
   - Tables: full-width, data-dense, monospace

5. **Apply Tokens** — Theme color_tokens, 8px spacing, Space Grotesk/Inter/JetBrains Mono

6. **Responsive Check** — Verify at all breakpoints

7. **Accessibility + Consistency** — Run `auditA11y` and `checkConsistency`

8. **Persist** — Call `generatePage` then `publishArtifact`

## Chart Colors
- Single data series: use `--primary` only
- Multi-series: `--primary`, `--secondary`, `--accent` (max 3 colors)
- Never rainbow — never per-item color arrays
- Axis labels: `--muted-foreground`, grid lines: `--border`
