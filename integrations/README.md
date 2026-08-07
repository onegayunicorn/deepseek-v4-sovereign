# SOVEREIGN — Integrations

Every recent OGU project is registered as a **connected project**: its role,
integration surface, and adapter are indexed in `registry.yaml`, verified by
`connector.py`, and documented in `projects/`.

```
mocking-jay ─────────────────────── digital twin (33 agent-nodes, quantum sim)
photonic-entanglement-engine ────── photonic entanglement subsystems
dna-unfolding-lab ───────────────── DNA simulations + agent workflows
codality ────────────────────────── coding platform OSA
universal-driver ────────────────── multi-platform device drivers (pnpm)
core ────────────────────────────── QLB v2.5 core (entanglement, Bloch, resonance, PVD)
drivers ─────────────────────────── C++ BCI drivers (muse, qlb arduino)
sensors ─────────────────────────── EEG / rPPG / thermal / touch / tremor / vocal
pipelines ───────────────────────── ancestral data + lineage ETL + resonance
buckets ─────────────────────────── multi-cloud object storage manager
kaleidoscope ────────────────────── intent decoding + persona generation
moodchroma ──────────────────────── biometric emotion pipeline
optogenetics ────────────────────── optogenetic control + photonic entanglement
skills ──────────────────────────── OGU agent skills (5)
website ─────────────────────────── QLB v2.5 dashboard
ogu-build ───────────────────────── TURMO + universal driver builds
onegayunicorn ───────────────────── Expanded Intelligence (scout→enhance→audit)
deploy ──────────────────────────── docker + nginx + systemd infra
```

## Usage

```bash
python3 integrations/connector.py            # connection report
python3 integrations/connector.py --json     # machine-readable
make status
```

## How projects connect

1. `registry.yaml` — canonical index (id, path, role, surface, flagship).
2. `connector.py` — verifies each path/surface exists and prints status.
3. `projects/<id>.md` — adapter doc: purpose, surface, wiring, entrypoints.
4. Runtime wiring — `src/sovereign/hardware.py`, `modules/integration-module.yaml`,
   and the task definitions (`tasks/lineage-sync.yaml`, `tasks/scout.yaml`) consume
   the registry to drive the connected capabilities.
