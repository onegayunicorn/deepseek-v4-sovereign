# Codality

**Role**: platform · **Path**: `../codality`

Coding platform OSA (complete, no stubs) — the codality open source
application.

## Integration surface

| Surface | Purpose |
|---|---|
| `codality_osa_complete_no_stubs/` | Complete OSA codebase |

## Wiring into SOVEREIGN

- Codality output feeds the coder agent benchmark loop (`tasks/code.yaml`).
- Candidate corpus source for the knowledge index (`jobs/corpus-index.yaml`).
