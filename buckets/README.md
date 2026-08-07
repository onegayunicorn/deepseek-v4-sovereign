# SOVEREIGN Buckets

Multi-cloud object storage layout for the orchestrator: raw telemetry,
model weights, artifacts, memory exports, audit trail, and backups.

```
sovereign-raw       ─ raw BCI/audio/sensor streams        (30d → IA, 90d → Glacier)
sovereign-models    ─ weights + adapters + quantizations  (180d → Glacier IR)
sovereign-artifacts ─ outputs, builds, reports, TTS       (60d → IA, 3y → expire)
sovereign-memory    ─ memory exports + knowledge docs     (90d → IA, 4y → expire)
sovereign-audit     ─ tamper-evident audit + compliance   (object lock, 7y)
sovereign-backup    ─ full snapshots                      (30d → Glacier, 5y)
```

## Usage

```bash
python3 buckets/bucket_bootstrap.py            # dry-run plan
python3 buckets/bucket_bootstrap.py --apply --env prod   # provision
```

## Integration

The bootstrap tries to load the OGU multi-cloud abstraction at
`../buckets/bucket_manager.py` (S3 / GCS / Azure unified interface with
checksums + retention). If unavailable it prints raw provider CLI commands.
