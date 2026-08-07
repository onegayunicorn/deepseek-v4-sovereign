#!/usr/bin/env bash
# SOVEREIGN — download/import model weights into models/
# Usage: bash scripts/import_models.sh [deepseek|fish|all]
set -euo pipefail
cd "$(dirname "$0")/.."

TARGET="${1:-all}"
: "${HF_TOKEN:?HF_TOKEN required for model downloads}"

import_deepseek() {
  echo "[models] DeepSeek-V4-Flash-0731 (metadata + specs; weights ~600GB — use snapshot_download)"
  python3 - <<'PY'
import os
from huggingface_hub import snapshot_download
snapshot_download(
    "deepseek-ai/DeepSeek-V4-Flash-0731",
    local_dir="models/deepseek-v4-flash-0731/weights",
    allow_patterns=["config.json", "tokenizer*", "generation_config.json", "*.safetensors.index.json"],
    token=os.environ["HF_TOKEN"],
)
PY
}

import_fish() {
  echo "[models] Fish Audio S2-Pro (weights ~20GB)"
  python3 - <<'PY'
import os
from huggingface_hub import snapshot_download
snapshot_download(
    "fishaudio/s2-pro",
    local_dir="models/fish-audio-s2-pro/weights",
    token=os.environ["HF_TOKEN"],
)
PY
}

case "$TARGET" in
  deepseek) import_deepseek ;;
  fish)     import_fish ;;
  all)      import_deepseek && import_fish ;;
  *) echo "unknown target: $TARGET (deepseek|fish|all)" >&2; exit 2 ;;
esac

echo "[models] import complete"
