# SOVEREIGN — Operational Manual

## Daily operations

```bash
make status          # orchestrator + hardware + integrations health
make test            # run the test suite
python3 -m sovereign.main status
```

## Operations catalog (see operations/)

| Operation | Script | When |
|---|---|---|
| Backup | `scripts/backup.sh` | Daily (cron) + before upgrades |
| Restore | `scripts/restore.sh` | Disaster recovery |
| Healthcheck | `scripts/healthcheck.sh` | Every 5 min (cron) |
| Migrate | `scripts/migrate.sh` | After version upgrade |
| Deploy | `scripts/deploy.sh` | Releases |
| Import models | `scripts/import_models.sh` | Model onboarding |

## Routine lifecycle

- **Lineage sync** runs daily 03:00 UTC (`triggers/cron/daily-lineage-sync.yaml`).
- **Health audit** runs hourly (`triggers/cron/hourly-health-audit.yaml`).
- **Memory pruning** enforces retention (`config/memory.yaml`).

## Incident response

| Symptom | First check | Escalation |
|---|---|---|
| Tasks failing repeatedly | `logs/executions/` + audit tail | Check agent state, raise max_retries |
| Hardware offline | `python3 -m sovereign.main status` | Re-pair ring/buds via BLE; check `hardware/` adapters |
| Bucket errors | `buckets/bucket_bootstrap.py` dry-run | Check provider creds + lifecycle |
| Audit chain mismatch | recompute prev_hash chain | Treat as tamper event; investigate |

## Backup & restore drill

```bash
bash scripts/backup.sh --target all            # daily
bash scripts/restore.sh --snapshot <id> --target all   # monthly drill
```

## Capacity planning

- SQLite state: grow `data/state/` on disk; archive via `sovereign-memory`
  bucket after 90 days.
- Vector store: `data/memory/vectors/` — prune per memory.yaml.
- Models: `models/` ≈ 600GB full / 150GB 8-bit per checkpoint (see
  `operations/import-models.yaml`).
