# 🌌 SOVEREIGN — DeepSeek-V4 Sovereign Orchestrator

> **Own your intelligence.** A self-hosted, privacy-preserving orchestration layer that routes
> work across sovereign AI models, agents, tools, and hardware — with full ownership of data,
> memory, and decision logs. Zero mandatory external calls. Air-gapped capable.

Built by **onegayunicorn (OGU)**, connected to the **Quantum Lineage Bridge**, **Mocking Jay
Universal Digital Twin**, and the full OGU project constellation.

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
│   DISTRIBUTION: APK / EXE / HF Spaces / GitHub Releases / winget / npm    │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## What this is

The **Sovereign Orchestrator** is a monorepo implementing the *DeepSeek-V4 Sovereign
Orchestrator* blueprint: a production-shaped, model-agnostic agent orchestration platform
that coordinates multiple DeepSeek-V4 model instances (chat / reasoner / coder / sovereign),
manages memory (working / episodic / semantic / procedural / vector), executes pluggable
tools under policy, streams a realtime API, and ships as desktop, mobile, and web products —
together with the **Sovereign Ring** BCI wearable and **Sovereign Buds** AI earbuds.

## Monorepo map

```
deepseek-v4-sovereign/
├── config/            # orchestrator, models, tools, permissions, memory, logging, security, network
├── src/sovereign/     # Python package: orchestrator, agents, memory, tools, governance, security,
│                      #   communication, knowledge, api, utils
├── agents/            # agent definitions (registry + sovereign + connected-project agents)
├── triggers/          # cron / event / webhook trigger definitions
├── tasks/             # task-type definitions
├── actions/           # action catalog
├── modules/           # module catalog
├── routines/          # routine definitions
├── operations/        # operation definitions
├── webhooks/          # github / huggingface / generic webhook definitions
├── jobs/              # job definitions
├── models/            # model registry + NEW sovereign AI model + DeepSeek-V4-Flash-0731 + Fish S2-Pro
├── buckets/           # multi-cloud bucket layout + bootstrap
├── builds/            # apk/ (Android) + exe/ (Windows) build pipelines
├── market/            # market plan, segments, channels
├── pitch/             # 12-slide investor deck + one-pager
├── avenue/            # 3 go-to-market avenues
├── brand/             # brand kit, voice, palette
├── xiaohongshu/       # zh-CN content (CES-optimized)
├── copy/              # platform-native marketing snippets
├── launch_plan.md     # T-21 → T+30 launch calendar
├── distribution/      # release channels, packaging, release pipeline
├── hardware/          # bci-ring/ + earbuds/ specs, firmware, driver adapters
├── integrations/      # registry + connector wiring ALL recent OGU projects
├── data/  logs/  tests/  scripts/  docs/  docker/  kubernetes/  frontend/
└── .github/workflows/ # ci / cd / security
```

## Component index

| Component | Location | What it is |
|---|---|---|
| Bucket | `buckets/` | Multi-cloud (S3/GCS/Azure) object storage layout for raw, models, artifacts, memory, audit |
| Agents | `agents/` + `src/sovereign/agents/` | Sovereign agents (chat/reasoner/coder/tool/coordinator/memory/supervisor) + connected-project agents |
| Triggers | `triggers/` | Cron, event, and webhook triggers that fire tasks |
| Tasks | `tasks/` | Typed task definitions (reason, code, search, plan, execute, coordinate) |
| Actions | `actions/` | Catalog of discrete actions agents can invoke |
| Modules | `modules/` | Pluggable capability modules (memory, knowledge, security, tts, bci) |
| Routines | `routines/` | Composable recurring routines (scout→enhance→audit, lineage sync) |
| Operations | `operations/` | Operational procedures (backup, healthcheck, migration, deploy) |
| Webhooks | `webhooks/` | GitHub, HuggingFace, and generic inbound webhook receivers |
| Jobs | `jobs/` | Long-running job definitions (training, indexing, TTS synthesis) |
| Models | `models/` | Registry + **Sovereign AI model** (derived from DeepSeek-V4-Flash-0731) + Fish Audio S2-Pro TTS |
| APK build | `builds/apk/` | Android Gradle project → `assembleDebug/Release` |
| EXE build | `builds/exe/` | PyInstaller one-file Windows build of the orchestrator CLI |
| Market | `market/` | Segment, TAM/SAM/SOM, channels, benchmarks |
| Pitch | `pitch/` | Investor deck + one-pager |
| Avenue | `avenue/` | 3 go-to-market avenues (OSS dev-first, health-tech DTC, enterprise B2B) |
| Brand | `brand/` | Brand kit, voice, palette (#0A0A10 / #00E5FF / #00FFCC) |
| Distribution | `distribution/` | Release channels, packaging, `release_pipeline.sh` |
| Hardware | `hardware/` | Sovereign Ring (BCI) + Sovereign Buds: specs, firmware, driver adapters |
| Integrations | `integrations/` | Connector wiring all recent OGU work (QLB, Mocking Jay, photonic engine, …) |

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
make test
```

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
  JWT auth, compliance checks.
- **Communication** — event bus (pub/sub), inter-agent messaging, MCP / A2A / OpenAI-compatible
  / gRPC protocol adapters.
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

## License

MIT — see [LICENSE](LICENSE). Model licenses: DeepSeek-V4-Flash-0731 (MIT), Fish Audio S2-Pro
(see model card).
