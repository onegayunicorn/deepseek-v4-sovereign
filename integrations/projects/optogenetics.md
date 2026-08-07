# Optogenetics

**Role**: control · **Path**: `../optogenetics`

Optogenetic controller with photonic entanglement and a global correction
protocol.

## Integration surface

| Surface | Purpose |
|---|---|
| `oi_controller.py` | Optogenetic intensity controller |
| `photonic_entanglement.py` | Photonic entanglement control |
| `global_correction_protocol.py` | Global correction |

## Wiring into SOVEREIGN

- `optogenetics` agent (control capabilities) for photonic intervention
  routines tied to ring/earbuds state.
- Correction protocol feeds the health-monitor routine.
