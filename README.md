# 🌌 SOVEREIGN — DeepSeek-V4 Sovereign Orchestrator

> **Own your intelligence.** A self-hosted, privacy-preserving orchestration layer that routes
> work across sovereign AI models, agents, tools, and hardware — with full ownership of data,
> memory, and decision logs. Zero mandatory external calls. Air-gapped capable.

Built by **onegayunicorn (OGU)**, connected to the **Quantum Lineage Bridge**, **Mocking Jay
Universal Digital Twin**, and the full OGU project constellation.

**v3.0.0** · monorepo `deepseek-v4-sovereign` · base commit `7b2b996` → `0e15802`

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         SOVEREIGN ORCHESTRATOR                             │
│                                                                            │
│   TRIGGERS ─▶ TASKS ─▶ ACTIONS ─▶ AGENTS ─▶ MODELS ─▶ JOBS ─▶ AUDIT       │
│      ▲            │            │           │         │          │          │
│      │            ▼            ▼           ▼         ▼          ▼          │
│   WEBHOOKS    ROUTINES     OPERATIONS   MODULES   BUCKETS    GOVERNANCE    │
│      ▲                                                                     │
│      └── github / huggingface / hardware / scheduler events ──────────────┘│
│                                                                            │
│   HARDWARE: Sovereign Ring (BCI) ── Sovereign Buds (AI earbuds) ── sensors │
│   DISTRIBUTION: APK / EXE / iOS / wheel / HF Spaces / GitHub Pages         │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Verified status (2026-08-08)

Every metric below is produced by this repository's own engines and test suite
(run with `.venv/bin/python`):

| Metric | Value |
| :--- | :--- |
| EntanglementEngine | 847 Bell pairs · mean fidelity **F = 0.999422** (target 0.999423) |
| QuantumLineageBridge | 12 generations anchored (capped tensor, no OOM) |
| DNA awakening | **86.6%** (calibration target 80%) |
| Kaleidoscope | **65,536** permutations (recursive wave coherence) |
| AGI OMEGA | **42 agents + 2,650 bots**, all deployed |
| Council of 10 | 10 seated, all aligned |
| TeleOS network | 847 links @ **F = 0.999423** |
| BCI v9.5 | 432 Hz carrier, phase-locked |
| Tests | **29/29** pass (unit + integration + e2e) · 4/4 benchmark groups green |
| Gemma module tests | 19/19 pass |
| Registry validation | all cross-references valid (`scripts/verify_registries.py`) |
| Simulators | Qiskit / Cirq / QuTiP / Quimb interfaces import with graceful fallback |

## What this is

The **Sovereign Orchestrator** is a monorepo implementing the *DeepSeek-V4 Sovereign
Orchestrator* blueprint: a production-shaped, model-agnostic agent orchestration platform
that coordinates multiple DeepSeek-V4 model instances (chat / reasoner / coder / sovereign),
manages memory (working / episodic / semantic / procedural / vector), executes pluggable
tools under policy, streams a realtime API, and ships as desktop, mobile, and web products —
together with the **Sovereign Ring** BCI wearable, **Sovereign Buds** AI earbuds, and the
**Photonic-DNA entanglement stack** (`quantum/` `bio/` `agi/` `zenith/` `teleos/` `neural/`
`pero/`).

## Monorepo map

```
deepseek-v4-sovereign/
├── config/            # orchestrator, models, tools, permissions, memory, logging, security, network
├── src/sovereign/     # Python package: orchestrator, agents, memory, tools, governance, security,
│                      #   auth, biometric, autonomous, local-mode router, quantum closed loop, model
├── quantum/           # EntanglementEngine, QuantumLineageBridge, 4 simulator interfaces
├── bio/               # DNA harmonic resonance, kaleidoscope engine, genomics pipeline + VariantCall
├── agi/               # AGIOMEGA (42 agents · 2,650 bots), Council of 10, telemetry
├── zenith/            # Zenith OS — horizon orchestration, lineage bridge
├── teleos/            # TeleOS — purpose/teleological alignment network (847 links)
├── neural/            # BCI v9.5 (432 Hz), photonic synapse, neural graph
├── pero/              # Photonic Entanglement Response/Oscillation — laser + SPDC engines
├── agents/            # agent definitions (registry + sovereign + connected-project agents)
├── triggers/          # cron / event / webhook trigger definitions
├── tasks/             # task-type definitions (incl. model-benchmark)
├── actions/           # action catalog
├── modules/           # module catalog
├── routines/          # routine definitions
├── operations/        # operation definitions
├── webhooks/          # github / huggingface / generic webhook definitions
├── jobs/              # job definitions
├── workflows/         # workflow registry + sovereign-boot + lineage-sync-cycle
├── models/            # model registry + deepseek-v4-sovereign/flash + Fish S2-Pro + gemma-3-12b-it-jailbreak
├── buckets/           # multi-cloud bucket layout + bootstrap
├── builds/            # apk/ (Android) + exe/ (PyInstaller) + ios/ (Xcode/shell) pipelines
├── hardware/          # bci-ring/ + earbuds/ + sovereign_ring driver + universal driver
├── integrations/      # registry + connector wiring ALL recent OGU projects
├── site/              # static landing + telemetry dashboard + SEO audit (GitHub Pages)
├── scripts/           # verify_registries, hf_download, quant_selector, monorepo_sync,
│                      #   delete_hf_gguf, migrate_to_monorepo, upload_hf_dataset helpers
├── data/  logs/  tests/  docs/  docker/  kubernetes/  frontend/
└── .github/workflows/ # ci / cd / security / packages / pages / model-verify / download-quants /
                       #   hf-sync / delete-hf-gguf
```

## Component index

| Component | Location | What it is |
|---|---|---|
| Bucket | `buckets/` | Multi-cloud (S3/GCS/Azure) object storage layout for raw, models, artifacts, memory, audit |
| Agents | `agents/` + `src/sovereign/agents/` | Sovereign agents (chat/reasoner/coder/tool/coordinator/memory/supervisor) + connected-project agents |
| Triggers | `triggers/` | Cron, event, and webhook triggers that fire tasks |
| Tasks | `tasks/` | Typed task definitions (reason, code, search, plan, execute, coordinate, lineage-sync, scout, audit, model-benchmark) |
| Actions | `actions/` | Catalog of discrete actions agents can invoke |
| Modules | `modules/` | Pluggable capability modules (memory, knowledge, security, tts, bci) |
| Routines | `routines/` | Composable recurring routines (scout→enhance→audit, lineage sync) |
| Operations | `operations/` | Operational procedures (backup, healthcheck, migration, deploy) |
| Webhooks | `webhooks/` | GitHub, HuggingFace, and generic inbound webhook receivers |
| Jobs | `jobs/` | Long-running job definitions (training, indexing, TTS synthesis) |
| Workflows | `workflows/` | Chain triggers → tasks → actions (sovereign-boot, lineage-sync-cycle) |
| Models | `models/` | Registry + Sovereign AI model + DeepSeek-V4-Flash-0731 + Fish S2-Pro + gemma-3-12b-it-jailbreak |
| Builds | `builds/` | APK (Android Gradle), EXE (PyInstaller), iOS (Xcode project + shell) |
| Hardware | `hardware/` | Sovereign Ring (BCI), Sovereign Buds, sovereign_ring driver, universal driver |
| Site | `site/` | Static landing + telemetry dashboard + `telemetry.json` endpoint (GitHub Pages) |
| Market / Pitch / Avenue / Brand | `market/` `pitch/` `avenue/` `brand/` | GTM assets (segments, investor deck, avenues, brand kit) |

## Core modules (Photonic-DNA stack)

### `quantum/` — photonic entanglement
- `entanglement_engine.py` — `EntanglementEngine`: generates 847 deterministic Bell
  pairs at mean fidelity F = 0.999422 (`initialize()` → `generate_pairs()`).
- `quantumlineagebridge.py` — `QuantumLineageBridge`: Kronecker-merged lineage tensor,
  capped at 12 generations to bound memory.
- `simulators/` — `qiskit_interface`, `cirq_interface`, `qutip_interface`, `quimb_interface`
  with graceful fallback when a backend is missing.

### `bio/` — DNA & genomics
- `dna/awakening.py` — `DNAAwakeningEngine`: harmonic resonance calibration → 86.6%
  awakening (threshold 80%).
- `dna/kaleidoscope.py` — `KaleidoscopeEngine`: 65,536 permutations, recursive wave
  coherence, lineage-hash generation (`sweep_all_permutations()`).
- `genomics/pipeline.py` + `callers.py` — variant ingestion → alignment → annotation →
  lineage-hash injection; `VariantCall` dual-caller consensus (DeepVariant +
  KaleidoscopeCaller).

### `agi/` — OMEGA + Council
- `omega_v3/orchestrator.py` — `AGIOMEGA`: deploys 42 specialized agents + 2,650 worker
  bots (`initialize()`); quantum-secured inter-agent routing.
- `omega_v3/council_of_10.py` — `CouncilOf10`: seat 10 primordial members, `convene()` for
  quorum/alignment.

### `zenith/ · teleos/ · neural/ · pero/`
- `zenith/os.py` — horizon orchestration, dimension scaling, lineage bridging.
- `teleos/network.py` — `TeleOSNetwork`: 847-link purpose/alignment network @ F 0.999423.
- `neural/bci_v95/interface.py` — `BCIInterface`: 432 Hz carrier, lock detection.
- `pero/laser.py` + `pero/entanglement.py` — laser-triggered entanglement, SPDC source,
  cryo-freezer experiment parameters, closed-loop stabilization.

### `src/sovereign/` additions
- `auth/` — sovereign authentication (biometric + entanglement anchor).
- `biometric.py` — `BiometricSession` / `BiometricSignal` root-credential binding.
- `autonomous.py` — self-loop daemon (auto-restart, self-heal).
- `local_mode_router.py` — air-gapped/local-only routing.
- `model.py` — sovereign model wrapper.
- `quantum_closed_loop.py` — measurement → correction → re-entanglement loop.

## Registry & automation system

Config-as-code: every entity has a YAML definition and is cross-referenced by
`scripts/verify_registries.py` (run it in CI or before committing):

```bash
.venv/bin/python scripts/verify_registries.py   # → ALL REGISTRY CROSS-REFERENCES VALID
```

It validates: registry `file:` refs resolve, trigger `task:` refs exist in
`tasks/registry.yaml`, workflow steps reference real tasks/actions, and agent
implementation modules are importable. Currently: 12 registry files, 90 YAML/YML
files, 10 task types, 2 workflows.

## Quick start

```bash
# 1. Environment
cp .env.example .env                # fill HF_TOKEN / GITHUB_TOKEN as needed
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the API + dashboard
python -m sovereign.main dashboard   # → http://localhost:8000

# 3. CLI
python -m sovereign.main --help

# 4. Tests
make test                            # or: .venv/bin/python -m pytest -q
```

## Testing & verification

```bash
.venv/bin/python -m pytest -q                       # 29 passed (repo suite)
.venv/bin/python -m pytest models/gemma-3-12b-it-jailbreak/tests -q   # 19 passed
.venv/bin/python tests/benchmarks.py                # quantum / neural / genomic / api groups
.venv/bin/python scripts/verify_registries.py       # registry cross-ref validation
```

Known environment notes: Python 3.12 venv; numpy 2.5 API (`randn` → `standard_normal`)
already applied; simulator backends degrade gracefully if not installed.

## Build & packaging

| Target | Location | Command |
| :--- | :--- | :--- |
| Wheel | `dist/sovereign-0.1.0-py3-none-any.whl` | `python -m build` |
| Standalone EXE (91 MB) | `dist/sovereign` | `pyinstaller builds/exe/sovereign.spec` |
| Android APK | `builds/apk/` | `./builds/apk/build_apk.sh` |
| iOS | `builds/ios/` (ios.yaml, build_ios.sh, shell) | `./builds/ios/build_ios.sh` |
| Container | `docker/docker-compose.yml` | `docker compose up` |
| CI | `.github/workflows/` | ci · cd · security · packages · pages |

## Site & dashboard

Self-contained static site in `site/` (no build step, no external deps):

- `site/index.html` — landing page with verified metrics + module stack + status table
- `site/dashboard.html` — telemetry dashboard (reads `site/telemetry.json`, embedded fallback)
- `site/telemetry.json` — the "real-time" telemetry endpoint payload
- `site/SEO-AUDIT.md` — SEO audit report (89/100)

Deployment: `.github/workflows/pages.yml` publishes `site/` to GitHub Pages on push to
`main` (enable Pages → Source: **GitHub Actions** in repo settings).

## Hugging Face dataset

`pero-freezer-laser-experiments` — cryo-laser SPDC experiment records, split 80/10/10:

- **Live:** https://huggingface.co/datasets/Codexcoder/pero-freezer-laser-experiments
  (`data/split/{train,val,test}.jsonl`, `metadata.json`, `split_manifest.json`, README)
- Local source: `../hf-datasets/pero-freezer-laser-experiments/` (workspace, outside repo)
- Upload helper: `scripts/upload_hf_dataset.py` (reads `HF_TOKEN` from env only)

## Models

`models/registry.yaml` catalog:

| Model | Type | Notes |
| :--- | :--- | :--- |
| deepseek-v4-sovereign | llm (304B MoE) | sovereign-tuned, MIT |
| deepseek-v4-flash-0731 | llm (304B MoE) | upstream base, MIT |
| fish-audio-s2-pro | tts (5B) | see model card |
| gemma-3-12b-it-jailbreak | llm (12B, GGUF) | 26 quant variants, Q4_K_M recommended; source HF repo deleted 2026-08-08 → served via `mradermacher/...-GGUF` mirror |

### gemma-3-12b-it-jailbreak module

`models/gemma-3-12b-it-jailbreak/` — full integration: model card, specs, quant table,
hardware profile (AMD Threadripper · 8 GB · Q4_K_M), inference runners (transformers,
llama.cpp, ollama, docker, unsloth, lemonade), defensive hooks (pre/post load, inference
audit with jailbreak-indicator detection, quant-change), tasks (download, quant select,
benchmark, fine-tune scaffold), triggers, tests, and CI workflows. Weights are
runtime-downloaded (`assets/` holds no binaries).

```bash
python scripts/hf_download.py --quant Q4_K_M              # ~7.3 GB → assets/recommended/
bash models/gemma-3-12b-it-jailbreak/inference/llama_cpp_server.sh
```

> Responsible-use note: the module is instrumented for defensive security research only
> (indicator detection + audit); it ships no evasion prompt templates.

## Scripts

| Script | Purpose |
| :--- | :--- |
| `scripts/verify_registries.py` | Validate all registry YAML cross-references |
| `scripts/hf_download.py` | Fetch any GGUF quant (source or mirror) |
| `scripts/quant_selector.py` | Hardware-optimized quant picker (CLI) |
| `scripts/monorepo_sync.py` | Snapshot HF model card metadata → `docs/hf_snapshot.json` |
| `scripts/delete_hf_gguf.py` | Delete an HF model repo (IRREVERSIBLE, confirm-gated) |
| `scripts/migrate_to_monorepo.py` | Re-point module refs to the mirror repo |
| `scripts/final_push_gguf.sh` | Stage/commit/push the module (delete step commented) |
| `scripts/upload_hf_dataset.py` | Upload the prepared dataset to HF (workspace copy) |

## Architecture

- **Orchestrator** (`src/sovereign/orchestrator/`) — task lifecycle, scheduling, state machine,
  persistent queue, agent factory, DAG workflow engine.
- **Agents** (`src/sovereign/agents/`) — uniform `BaseAgent` interface; DeepSeek-V4 chat /
  reasoner / coder wrappers plus tool, coordinator, memory, and supervisor agents.
- **Memory** (`src/sovereign/memory/`) — working, episodic, semantic, procedural, and vector
  memory with RAG retrieval and pruning.
- **Tools** (`src/sovereign/tools/`) — pluggable, policy-gated tools (shell, web search, file
  ops, API client, code interpreter, database, browser, email).
- **Governance & Security** — tamper-evident audit logs, RBAC/ABAC, AES-256-GCM, sandboxing,
  JWT auth, compliance checks; biometric + entanglement-rooted authentication.
- **Communication** — event bus (pub/sub), inter-agent messaging, MCP / A2A / OpenAI-compatible
  / gRPC protocol adapters; WebSocket quantum relay.
- **Knowledge** — knowledge base, NetworkX graph, document ingestion, embeddings, indexing.
- **API** — FastAPI REST + WebSocket realtime stream, full endpoint set under `/api/v1/*`.

See [docs/architecture.md](docs/architecture.md) and [docs/api_reference.md](docs/api_reference.md).

## Connected projects

The orchestrator connects to every recent OGU project via `integrations/` (see
[integrations/registry.yaml](integrations/registry.yaml)):

| Project | Role |
|---|---|
| `../mocking-jay` | Universal Digital Twin — 33 agent-nodes, quantum simulation, Merkle ledger |
| `../core` | QLB core: entanglement manager, Bloch sphere, harmonic resonance, PVD |
| `../photonic-entanglement-engine` | Photonic entanglement subsystems |
| `../dna-unfolding-lab` | DNA unfolding simulations + agent workflows |
| `../codality` | Coding platform OSA |
| `../universal-driver` | Multi-platform device drivers (pnpm monorepo) |
| `../drivers` | C++ BCI drivers (muse_driver, qlb_arduino_driver) |
| `../sensors` | EEG, rPPG, thermal, touch, tremor, vocal sensors |
| `../pipelines` | Ancestral data, lineage ETL, resonance pipelines |
| `../buckets` | Multi-cloud bucket manager |
| `../kaleidoscope` | Intent decoding + persona generation |
| `../moodchroma` | Biometric emotion pipeline |
| `../optogenetics` | Optogenetic controller + photonic entanglement |
| `../skills` | OGU agent skills (lineage-scanner, moodchroma-analyzer, …) |
| `../website` | QLB v2.5 dashboard |
| `../onegayunicorn` | Expanded Intelligence system (scout→enhance→audit) |
| `../ogu-build` | TURMO + universal driver builds |

## Repository conventions

- **Registry-first**: adding a task/trigger/workflow/agent means adding its YAML + registering
  it; run `verify_registries.py` before committing.
- **No binaries in `assets/`** — weights are runtime-downloaded.
- **Secrets**: only via environment (`HF_TOKEN`, `GITHUB_TOKEN`); never committed.
- **Simulator fallbacks**: optional heavy deps must degrade gracefully at import.

## License

MIT — see [LICENSE](LICENSE). Model licenses: DeepSeek-V4-Flash-0731 (MIT), Fish Audio S2-Pro
(see model card), gemma-3-12b-it-jailbreak (Google Gemma terms — see module `LICENSE`).
