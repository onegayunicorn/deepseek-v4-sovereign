# DNA Unfolding Lab

**Role**: simulation · **Path**: `../dna-unfolding-lab`

DNA unfolding simulations with a dedicated agent + workflow + sandbox stack.

## Integration surface

| Surface | Purpose |
|---|---|
| `src/` | Unfolding simulation core |
| `agents/` | Simulation agents |
| `workflows/` | Workflow definitions |
| `tasks/` | Task definitions |
| `sandbox/` | Sandboxed execution |
| `config/` | Lab config |

## Wiring into SOVEREIGN

- `dna-lab` agent exposes DNA simulation capability.
- Runs inside the sovereign sandbox tool (`security/sandbox.py`).
- Participates in the daily lineage-sync routine.
