#!/usr/bin/env bash
# Final Push — gemma-3-12b jailbreak module to monorepo
# NOTE: step 1 deletes the HF repo (IRREVERSIBLE). Run it deliberately.
set -euo pipefail

# 1. Delete HF GGUF repo (optional — uncomment when ready, confirm first)
# echo "Deleting HF GGUF repository..."
# python scripts/delete_hf_gguf.py --repo Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF --force

# 2. Add to monorepo
git add models/gemma-3-12b-it-jailbreak/
git add scripts/
git add .github/workflows/

# 3. Commit
git commit -m "feat: add gemma-3-12b-it-jailbreak-EN-i1-GGUF — full monorepo integration

- Complete model specs and quantization table (26 variants)
- Hardware-optimized Q4_K_M for AMD Threadripper (8GB)
- Inference runners (llama.cpp, ollama, docker, unsloth, lemonade, transformers)
- Defensive hooks (pre/post load, inference audit, quant change)
- Tasks: download, quant selection, benchmark, fine-tune scaffold
- Triggers: model load, inference complete, quant change
- Test suite (import/quant/inference/hardware fit/jailbreak detection)
- CI: model-verify, download-quants, hf-sync, delete-hf-gguf
- Registered in models/registry.yaml"

# 4. Push
git push origin main

echo "DONE — https://github.com/onegayunicorn/deepseek-v4-sovereign"
