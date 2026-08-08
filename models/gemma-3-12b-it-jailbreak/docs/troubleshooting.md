# Troubleshooting — gemma-3-12b-it-jailbreak

| Symptom | Cause / fix |
| :--- | :--- |
| `Model file not found` (pre-load) | Weights not downloaded — run `python scripts/hf_download.py --quant Q4_K_M` |
| `403 Forbidden: storage space` (HF) | Account public storage quota full — free quota (delete/archive a repo) or upgrade |
| OOM / swap thrash on 8 GB | Q4_K_M is at the edge; drop to `Q4_K_S`/`IQ4_XS` or use `--ctx-size 1024` |
| `llama` command not found | Install: `curl -LsSf https://llama.app/install.sh \| sh` |
| Slow tokens/s | CPU-only 12B — expect 1–5 tok/s; use Q3_K_M or smaller ctx for speed |
| Source HF repo deleted | Re-point to mirror: `python scripts/migrate_to_monorepo.py --apply`, then download from `mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF` |
| ImportError torch/transformers | `pip install transformers torch huggingface_hub` |
