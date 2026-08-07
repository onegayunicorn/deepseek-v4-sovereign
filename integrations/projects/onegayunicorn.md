# onegayunicorn — Expanded Intelligence System

**Role**: intelligence · **Flagship** ★ · **Path**: `../onegayunicorn`

**Scout. Enhance. Audit. Repeat.** — autonomous multi-agent loop over GitHub
repositories with a bio-quantum priority matrix, webhook/trigger/task
machinery, and a dark-theme dashboard.

## Integration surface

| Surface | Purpose |
|---|---|
| `main.py` | Entry — boots runtime, wires everything, runs the loop |
| `core/` | Runtime, bio-quantum, scout, intelligence, enhancer, auditor, events |
| `config/` | YAML config + env override loader |
| `web/` | SSE dashboard |
| `workflows/` | YAML DAG execution |
| `reports/` | Audit reports |

## Wiring into SOVEREIGN

- SOVEREIGN's `scout`/`audit` tasks wrap the OGU scout→enhance→audit loop.
- `agents/connected-projects.agent.yaml` → `ogu-intelligence` agent.
- Routines: `scout-enhance-audit.yaml` mirrors the loop with sovereign
  task primitives.
