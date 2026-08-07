# QLB Core (Quantum Lineage Bridge v2.5)

**Role**: qlb-core · **Flagship** ★ · **Path**: `../core`

The QLB v2.5 engine core: activation score, Markovian descent, Bloch sphere,
harmonic resonance, entanglement manager, information geometry, PVD engine.

## Integration surface

| Surface | Purpose |
|---|---|
| `entanglement_manager.py` | Entanglement pair management |
| `bloch_sphere.py` | Quantum state visualization math |
| `harmonic_resonance_engine.py` | Resonance engine |
| `pvd_engine.py` | PVD processing |
| `activation_score.py` | Activation scoring |
| `markovian_descent.py` | Markovian descent |
| `information_geometry.py` | Information geometry |

## Wiring into SOVEREIGN

- `qlb-core` agent exposes the full engine capability set.
- Coherence/resonance state can gate hardware (ring) streaming priority.
- `pipelines/` consume core engines via `tasks/lineage-sync.yaml`.
