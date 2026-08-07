#!/usr/bin/env bash
# SOVEREIGN — development mode with reload
set -euo pipefail
cd "$(dirname "$0")/.."

export SOVEREIGN_MODE="${SOVEREIGN_MODE:-development}"
export LOG_LEVEL="${LOG_LEVEL:-DEBUG}"

if [ ! -d .venv ]; then
  echo "[SOVEREIGN] creating venv ..."
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "[SOVEREIGN] dev server on :8000 (reload on)"
exec .venv/bin/uvicorn sovereign.main:app --host 0.0.0.0 --port 8000 --reload --app-dir src
