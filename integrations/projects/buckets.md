# OGU Bucket Manager

**Role**: storage · **Path**: `../buckets`

Multi-cloud object storage abstraction (AWS S3 / GCP GCS / Azure Blob) with
checksums, lifecycle, and retention enforcement.

## Integration surface

| Surface | Purpose |
|---|---|
| `bucket_manager.py` | Unified `BucketManager` API |
| `bucket_config.yaml` | Cloud layout (raw-bci, models, artifacts, ...) |
| `ancestral_archiver.py` | Archival pipeline |

## Wiring into SOVEREIGN

- `buckets/bucket_bootstrap.py` provisions the sovereign bucket layout
  through this manager (`--apply`).
- Backup operation (`operations/backup.yaml`) targets `sovereign-backup`.
