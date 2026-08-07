# OGU Pipelines

**Role**: etl · **Path**: `../pipelines`

Data pipelines: ancestral data, lineage ETL, resonance pipeline, and the
pipeline orchestrator.

## Integration surface

| Surface | Purpose |
|---|---|
| `ancestral_data_pipeline.py` | Ancestral data processing |
| `lineage_etl.py` | Lineage extraction/transform/load |
| `resonance_pipeline.py` | Resonance pipeline |
| `pipeline_orchestrator.py` | Pipeline orchestration |

## Wiring into SOVEREIGN

- `tasks/lineage-sync.yaml` references all three pipelines.
- `triggers/cron/daily-lineage-sync.yaml` runs them daily.
- Outputs land in `data/artifacts/outputs/`.
