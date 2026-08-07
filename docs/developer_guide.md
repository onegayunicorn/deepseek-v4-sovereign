# SOVEREIGN — Developer Guide

## Layout

| Path | Contents |
|---|---|
| `src/sovereign/` | Python package (orchestrator, agents, memory, tools, governance, security, communication, knowledge, api, utils) |
| `config/` | YAML configuration (8 files) |
| `agents/ triggers/ tasks/ actions/ modules/ routines/ operations/ webhooks/ jobs/` | Declarative runtime definitions |
| `models/` | Model registry + sovereign model |
| `buckets/` | Bucket layout + bootstrap |
| `builds/` | APK + EXE pipelines |
| `distribution/` | Release channels + pipeline |
| `hardware/` | Ring + earbuds specs, firmware, adapters |
| `integrations/` | Connected OGU projects |
| `brand/ market/ pitch/ avenue/ xiaohongshu/ copy/` | GTM + brand |
| `docs/ scripts/ docker/ kubernetes/ frontend/ tests/` | Ops + UI |

## Adding a tool

1. Add a function in `src/sovereign/tools/builtin/` (or a module in
   `tools/custom/`).
2. Register it in `tools/registry.py::_load_builtin` (or via `ToolSpec`
   in a custom module).
3. Declare it in `config/tools.yaml` + `config/permissions.yaml`
   (roles/ACL).
4. It is now available through the executor + `/api/v1/tools/execute`.

## Adding an agent kind

1. Subclass `BaseAgent` in `src/sovereign/agents/`.
2. Add a branch in `orchestrator/agent_factory.py::create`.
3. Declare in `agents/sovereign-core.agent.yaml`.

## Adding a connected project

1. Add an entry to `integrations/registry.yaml` (id, path, role, surface).
2. Write `integrations/projects/<id>.md`.
3. Run `python3 integrations/connector.py` to verify.

## Tests

```bash
make test                                  # pytest
python3 -m py_compile <file>               # single-file syntax check
```

## Conventions

- Python 3.11+, stdlib-first in core modules; heavy deps optional/guarded.
- All subsystems raise typed exceptions from `utils/errors.py`.
- YAML configs are the source of truth; code reads via `Config.load()`.
- Emit audit events for anything that changes state.
