# SOVEREIGN — Troubleshooting

## Startup / imports

| Symptom | Cause | Fix |
|---|---|---|
| `No module named 'sovereign'` | PYTHONPATH missing | `export PYTHONPATH=src` or run from monorepo root |
| `PyYAML is required` | optional dep missing | `pip install pyyaml` |
| `no encryption key configured` | `AES_KEY_B64` unset | set in `.env` (32-byte base64) |
| FastAPI import error | deps not installed | `pip install -r requirements.txt` |

## Orchestrator

| Symptom | Cause | Fix |
|---|---|---|
| Tasks stuck `pending` | processor loop not started | ensure `await orchestrator.start()` |
| Illegal transition error | state machine misuse | transitions: pending→running→completed/failed/cancelled |
| Task retries forever | max_retries too high / agent always fails | check `logs/executions/task_{id}.log` |

## Hardware

| Symptom | Cause | Fix |
|---|---|---|
| No ring/buds in status | adapter not found or import failed | check `hardware/bci-ring/driver_adapter.py`; BLE pairing |
| Stub stream active | driver/sensor deps missing (e.g. scipy) | install sensor deps; adapters degrade gracefully |

## Model inference

| Symptom | Cause | Fix |
|---|---|---|
| 503 from HF router | model loading | retry after `estimated_time`; do not spam |
| Local echo responses | no base_url/api_key | set `OPENAI_BASE_URL`/`HF_ROUTER_URL` + `HF_TOKEN` |
| OOM on vLLM | wrong quantization | use INT8/FP8 flags in `models/deepseek-v4-sovereign/README.md` |

## Integrations

| Symptom | Cause | Fix |
|---|---|---|
| Connector reports missing | registry surface mismatch | adjust `integrations/registry.yaml` |
| `bucket_manager` import fails | boto3 etc. absent | install cloud SDK or use `--apply` fallback CLI notes |

## Still stuck?

Open an issue with: `make status` output, `logs/audits/audit.jsonl` tail,
and the failing command.
