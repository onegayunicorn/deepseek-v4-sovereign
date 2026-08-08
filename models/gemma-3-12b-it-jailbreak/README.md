# Gemma-3-12B Jailbreak (GGUF) — Sovereign module

Local module card for the quantized jailbreak/red-teaming variant of
Gemma-3-12B, integrated into the Sovereign monorepo.

- **Source (HF):** `Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF`
- **Mirror (static quants):** `mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF`
- **Lineage:** google/gemma-3-12b-pt → google/gemma-3-12b-it →
  alexwirrell/gemma-3-12b-it-jailbreak-EN → this GGUF
- **Recommended quant:** `Q4_K_M` (7.3 GB) — fits 8 GB RAM
- **License:** Google Gemma license — see [LICENSE](LICENSE) and
  https://ai.google.dev/gemma/terms

## Layout

```
inference/     loaders + runners (transformers, llama.cpp, ollama, docker, unsloth, lemonade)
config/        hardware profile, model config, quantization presets (26 variants), inference settings
hooks/         pre/post load + inference/quantization instrumentation (defensive)
tasks/         download, quant selection, benchmark, fine-tune scaffolding
triggers/      event wiring (load, inference, quant change)
tests/         import/quant/inference/hardware checks
assets/        runtime-downloaded weights (NOT committed)
blueprints/    lineage tree, fine-tuning chain, research scope, integration plan
```

## Quick start

```bash
# download the recommended quant (runtime, ~7.3 GB)
huggingface-cli download Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF \
  --include "*Q4_K_M.gguf" --local-dir models/gemma-3-12b-it-jailbreak/assets/recommended/

# run via llama.cpp (fastest on CPU)
llama serve -hf Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF:Q4_K_M
```

## Usage notes

- This module is instrumented for **defensive** security research:
  inference hooks log and flag jailbreak-indicator prompts (audit trail),
  they do not generate or amplify evasive content.
- `assets/` holds no binaries — weights are downloaded at runtime by
  `scripts/hf_download.py` or `tasks/download_model.py`.
