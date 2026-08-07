# SOVEREIGN — API Reference

Base URL: `http://localhost:8000` · OpenAPI: `/docs` · Realtime: `/ws/events`

## Endpoints

### System
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness + queue/agent counters |
| GET | `/api/v1/system/health` | Full orchestrator health |
| GET | `/api/v1/system/metrics` | Metrics snapshot |
| GET | `/api/v1/system/metrics/prometheus` | Prometheus text format |
| GET | `/api/v1/system/info` | Brand + version + palette |

### Tasks
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/tasks/` | Submit task `{type, payload, priority, max_retries}` |
| GET | `/api/v1/tasks/` | List (status/limit/offset) |
| GET | `/api/v1/tasks/{id}` | Get task |
| DELETE | `/api/v1/tasks/{id}` | Cancel task |
| POST | `/api/v1/tasks/{id}/retry` | Retry failed task |
| GET | `/api/v1/tasks/{id}/result` | Completed result |

### Agents
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/agents/` | List agents + status |
| GET | `/api/v1/agents/{id}` | Agent detail |
| POST | `/api/v1/agents/{id}/restart` | Restart agent |

### Memory
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/memory/store` | Store `{memory_type, key, value}` |
| GET | `/api/v1/memory/{type}/{key}` | Retrieve |
| POST | `/api/v1/memory/search` | Search `{query, k}` |
| GET | `/api/v1/memory/stats` | Memory statistics |

### Tools
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/tools/` | Registered tools |
| POST | `/api/v1/tools/execute` | Execute `{tool, arguments, role}` |

### Knowledge
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/knowledge/ingest` | Ingest document |
| POST | `/api/v1/knowledge/search` | Semantic search |
| POST | `/api/v1/knowledge/graph` | Add triple |
| GET | `/api/v1/knowledge/stats` | KB statistics |

### Governance
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/governance/audit` | Recent audit records |
| GET | `/api/v1/governance/audit/export` | Export (jsonl/csv) |
| GET | `/api/v1/governance/roles` | RBAC roles/permissions |
| GET | `/api/v1/governance/compliance` | GDPR/SOC2 sweep |

## WebSocket

```
GET /ws/events
```
Streams orchestrator events (`task.completed`, `agent.state_changed`, ...);
replays last 25 events on connect.

## Example

```bash
curl -s -X POST localhost:8000/api/v1/tasks/ \
  -H 'content-type: application/json' \
  -d '{"type":"reason","payload":{"input":"analyze Q3 lineage delta"}}'
# → {"id":"task_...","type":"reason","status":"pending",...}
```
