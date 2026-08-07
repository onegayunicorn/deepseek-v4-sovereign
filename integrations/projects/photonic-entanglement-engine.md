# Photonic Entanglement Engine

**Role**: quantum · **Flagship** ★ · **Path**: `../photonic-entanglement-engine`

Photonic entanglement subsystems: agent swarm, hub, skills, and website for
entanglement-based coordination.

## Integration surface

| Surface | Purpose |
|---|---|
| `src/` | Entanglement engine implementation |
| `agents/` | Entanglement agents |
| `hub/` | Coordination hub |
| `skills/` | Entanglement skills |
| `website/` | Project site |
| `pyproject.toml`, `setup.py` | Packaging |

## Wiring into SOVEREIGN

- Exposed as the `photonic-engine` agent (photonic entanglement capability).
- Feeds `tasks/lineage-sync.yaml` (engines: photonic + dna).
- TTS/bci modules can consume entanglement state for coherence scoring.
