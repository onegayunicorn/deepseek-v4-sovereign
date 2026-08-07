# OGU Skills

**Role**: skills · **Path**: `../skills`

Agent skills harvested from OGU workflows: lineage scanning, moodchroma
analysis, optogenetic control, quantum lineage bridge, resonance monitoring.

## Integration surface

| Surface | Purpose |
|---|---|
| `lineage-scanner/` | Lineage scanning skill |
| `moodchroma-analyzer/` | Mood analysis skill |
| `optogenetic-controller/` | Optogenetic control skill |
| `quantum-lineage-bridge/` | QLB skill |
| `resonance-monitor/` | Resonance monitoring skill |

## Wiring into SOVEREIGN

- Skill registry is a candidate source for `agents/connected-projects`.
- SOVEREIGN routines may invoke these skills for lineage/resonance work.
