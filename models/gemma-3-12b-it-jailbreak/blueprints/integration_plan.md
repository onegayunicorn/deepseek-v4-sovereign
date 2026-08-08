# Integration Plan — gemma-3-12b into Sovereign

How this module wires into the existing Sovereign monorepo.

## Dependencies
- `models/registry.yaml` — module registered (`gemma-3-12b-it-jailbreak`).
- `quantum/` `bio/` `agi/` — the model can be consumed as an additional
  inference backend by the AGI fleet (`agi/agents/inference_agent.py`
  can route to this module's unified loader).
- `triggers/registry.yaml` pattern — module-local triggers follow the same
  event schema (model.loaded, inference.complete, quant.changed).

## Flow
1. `scripts/hf_download.py --quant Q4_K_M` → `assets/recommended/`
2. `hooks/pre_load.py` validates file/RAM/quant/deps
3. `inference/model_loader.py` loads via selected backend
4. `hooks/on_inference.py` records metrics + audit flags
5. `triggers/on_inference_complete.yaml` broadcasts results

## CI
- `model-verify.yml` — runs the test suite on push
- `download-quants.yml` — caches quant metadata in CI
- `hf-sync.yml` — syncs model card metadata with HF
- `delete-hf-gguf.yml` — manual (workflow_dispatch) HF repo deletion with
  explicit `DELETE` confirmation input

## Migration
If the HF source repo (`Codexcoder/...-GGUF`) is deleted to free quota,
update `config/model_config.yaml` + download scripts to point at the mirror
`mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF` (static quants, same files).
