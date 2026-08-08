#!/usr/bin/env bash
# Unsloth Studio — macOS / Linux / WSL
# Usage: ./unsloth_studio.sh [PORT]
set -euo pipefail
PORT="${1:-8888}"

if ! command -v unsloth >/dev/null 2>&1; then
  echo "unsloth not found. Install: curl -fsSL https://unsloth.ai/install.sh | sh" >&2
  exit 1
fi

unsloth studio -H 0.0.0.0 -p "${PORT}"
echo "Open http://localhost:${PORT} → search: mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF"
