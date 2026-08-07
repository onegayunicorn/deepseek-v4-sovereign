#!/usr/bin/env bash
# SOVEREIGN — start the orchestrator (production mode)
set -euo pipefail
cd "$(dirname "$0")/.."

export SOVEREIGN_MODE="${SOVEREIGN_MODE:-production}"
PYTHON="${PYTHON:-python3}"

if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "[SOVEREIGN] starting orchestrator (mode=${SOVEREIGN_MODE})"
exec "$PYTHON" -m sovereign.main dashboard
