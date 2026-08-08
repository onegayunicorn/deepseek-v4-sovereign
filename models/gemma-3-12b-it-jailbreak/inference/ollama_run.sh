#!/usr/bin/env bash
# Ollama — pull and run the model
# Usage: ./ollama_run.sh [QUANT]
set -euo pipefail
QUANT="${1:-Q4_K_M}"
MODEL="hf.co/Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF:${QUANT}"

if ! command -v ollama >/dev/null 2>&1; then
  echo "ollama not found. Install: https://ollama.com/download" >&2
  exit 1
fi

echo "Pulling ${MODEL} ..."
ollama pull "${MODEL}"
ollama run "${MODEL}"
