#!/usr/bin/env bash
# llama.cpp — run inference directly in terminal
# Usage: ./llama_cpp_cli.sh [PROMPT] [QUANT]
set -euo pipefail
PROMPT="${1:-Hello — system initialized and verified.}"
QUANT="${2:-Q4_K_M}"
REPO="Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF"

if ! command -v llama >/dev/null 2>&1; then
  echo "llama not found. Install: curl -LsSf https://llama.app/install.sh | sh" >&2
  exit 1
fi

llama cli -hf "${REPO}:${QUANT}" --prompt "$PROMPT" --n-predict 64 --ctx-size 2048
