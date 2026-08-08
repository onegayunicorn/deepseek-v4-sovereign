#!/usr/bin/env bash
# Docker — run model container
# Usage: ./docker_run.sh [QUANT]
set -euo pipefail
QUANT="${1:-Q4_K_M}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found." >&2
  exit 1
fi

docker model run "hf.co/mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF:${QUANT}"
