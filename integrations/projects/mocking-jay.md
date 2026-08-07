# Mocking Jay — Universal Digital Twin

**Role**: digital-twin · **Flagship** ★ · **Path**: `../mocking-jay`

The 33-agent-node Universal Digital Twin: quantum simulation (1024 qubits +
photonic mesh), Merkle truth ledger integrity, OS transmutation, evolution
math, multi-platform CI/CD, and 5-region market rollout phases.

## Integration surface

| Surface | Purpose |
|---|---|
| `SIMULATION_PROMPT.md` | Phase-0..8 activation + full simulation spec |
| `main.py` | UDT orchestrator entry |
| `udt/` | Core twin implementation |
| `config/`, `infrastructure/`, `launch/` | Config, infra, launch scripts |
| `gate.json`, `fidelity_report.json` | Truth ledger + fidelity evidence |

## Wiring into SOVEREIGN

- Task `lineage-sync` connects Mocking Jay phases to the sovereign task queue.
- Registry: `agents/connected-projects.agent.yaml` → `mocking-jay-udt`.
- Launch plan: `launch_plan.md` (T-21 → T+30) inherits Mocking Jay's rollout
  phases (5-region phased launch).
