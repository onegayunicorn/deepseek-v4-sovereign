#!/usr/bin/env bash
# llama.cpp — start local OpenAI-compatible server + Web UI
# Usage: ./llama_cpp_server.sh [QUANT]   (default Q4_K_M)
set -euo pipefail
QUANT="${1:-Q4_K_M}"
REPO="mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF"

if ! command -v llama >/dev/null 2>&1; then
  echo "llama not found. Install: curl -LsSf https://llama.app/install.sh | sh" >&2
  exit 1
fi

echo "Starting llama.cpp server: ${REPO}:${QUANT}"
llama serve -hf "${REPO}:${QUANT}"
