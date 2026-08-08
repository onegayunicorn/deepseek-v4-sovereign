# assets/recommended/

Runtime-downloaded weights — nothing is committed here (the Q4_K_M GGUF is
~7.3 GB and is fetched on demand).

```bash
# from the repo root
python scripts/hf_download.py --quant Q4_K_M
# or directly
huggingface-cli download Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF \
  --include "*Q4_K_M.gguf" --local-dir models/gemma-3-12b-it-jailbreak/assets/recommended/
```
