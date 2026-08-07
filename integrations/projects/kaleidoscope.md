# Kaleidoscope

**Role**: intent · **Path**: `../kaleidoscope`

Intent decoding, persona generation, outcome scoring, and simulation
running.

## Integration surface

| Surface | Purpose |
|---|---|
| `intent_decoder.py` | Decode user intent |
| `persona_generator.py` | Generate personas |
| `outcome_scoring.py` | Score outcomes |
| `simulation_runner.py` | Run simulations |
| `kaleidoscope_engine.py` | Engine entry |

## Wiring into SOVEREIGN

- `kaleidoscope` agent (intent/persona capabilities) assists the
  coordinator agent's goal decomposition.
- Persona output feeds the marketing pipeline (`brand/`, `copy/`).
