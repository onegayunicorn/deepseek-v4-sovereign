#!/usr/bin/env bash
# Lemonade — pull and run the model
# Usage: ./lemonade_run.sh [QUANT]
set -euo pipefail
QUANT="${1:-Q4_K_M}"
TAG="user.gemma-3-12b-it-jailbreak-EN-i1-GGUF-${QUANT}"

if ! command -v lemonade >/dev/null 2>&1; then
  echo "lemonade not found." >&2
  exit 1
fi

lemonade pull "Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF:${QUANT}"
lemonade run "${TAG}"
