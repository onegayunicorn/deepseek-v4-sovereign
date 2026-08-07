# Changelog

All notable changes to SOVEREIGN — DeepSeek-V4 Sovereign Orchestrator.

## [0.1.0] — 2026-08-07

### Added
- **Orchestrator core** (`src/sovereign`): task lifecycle with retry, priority queue
  (memory/SQLite), scheduler (cron/interval/event), DAG workflow engine, state machines.
- **Agents**: DeepSeek-V4 chat / reasoner / coder wrappers, tool agent (policy-gated),
  coordinator, memory agent, supervisor. Sovereign local fallback (no API key needed).
- **Memory**: working (TTL), episodic (SQLite), semantic (triples), procedural,
  vector (memory/chroma) + RAG retrieval with sovereign hash-placeholder embeddings.
- **Tools**: shell (sandboxed allow-list), web_search (sovereign-local default),
  file_ops, api_client (allow-listed), code_interpreter (import-blocked), database,
  browser + email (disabled by default).
- **Governance & Security**: tamper-evident hash-chained audit log, RBAC/ABAC
  permissions, policy engine, ethics guardrails, compliance (GDPR/SOC2), AES-256-GCM
  encryption, keyring, JWT auth, sandboxing.
- **Communication**: event bus, inter-agent message bus, MCP / A2A / OpenAI-compatible /
  gRPC protocol adapters.
- **Knowledge**: knowledge base, NetworkX graph, document ingestion, embeddings, query.
- **API**: FastAPI REST + WebSocket event stream, jobs, webhooks (GitHub/HF/generic),
  hardware telemetry, integrations endpoint.
- **Declarative registries**: agents, triggers, tasks, actions, modules, routines,
  operations, webhooks, jobs (all YAML).
- **Models**: NEW sovereign AI model card (304B MoE, DSpark, 1M ctx, MIT) + DeepSeek-V4-
  Flash-0731 specs/benchmarks/API examples + Fish Audio S2-Pro TTS client.
- **Buckets**: 6-bucket multi-cloud layout + bootstrap (S3/GCS/Azure).
- **Builds**: Android Gradle project (APK) + PyInstaller onefile (EXE/Linux).
- **Distribution**: 7 release channels, packaging guide, release pipeline.
- **Hardware**: Sovereign Ring (BCI) + Sovereign Buds — specs, firmware, driver
  adapters bridging the OGU driver/sensor stack.
- **Brand & GTM**: brand kit, market plan, 12-slide pitch, 3 avenues, launch plan,
  Xiaohongshu content, platform copy.
- **Integrations**: connector + registry wiring 18 connected OGU projects.
- **Platform**: Docker, Kubernetes, docs, tests, CI/CD workflows, dark dashboard.

### Fixed
- PyInstaller spec path resolution (`../../src` from `builds/exe/`).
- APK build skips gracefully when the Android toolchain is absent.
