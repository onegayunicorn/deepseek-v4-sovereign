# QLB v2.5 Website / Dashboard

**Role**: dashboard · **Path**: `../website`

Dark-theme QLB v2.5 dashboard (Chart.js, #0A0A10 / #00E5FF / #00FFCC) —
the visual surface for the OGU system.

## Integration surface

| Surface | Purpose |
|---|---|
| `index.html` | Single-file dashboard (QLB v2.5) |

## Wiring into SOVEREIGN

- SOVEREIGN's own frontend (`frontend/`) follows the same design tokens.
- Dashboard data endpoints map to `/api/v1/system/*` and `/ws/events`.
