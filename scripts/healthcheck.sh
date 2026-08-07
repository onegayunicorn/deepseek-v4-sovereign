#!/usr/bin/env bash
# SOVEREIGN — health check
# Exit codes: 0 ok · 1 degraded · 2 down
set -uo pipefail
cd "$(dirname "$0")/.."

HOST="${SOVEREIGN_HOST:-localhost}"
PORT="${SOVEREIGN_PORT:-8000}"
FAIL=0

echo "[health] api probe http://${HOST}:${PORT}/health"
if curl -sf --max-time 5 "http://${HOST}:${PORT}/health" > /dev/null 2>&1; then
  echo "[health] api: OK"
else
  echo "[health] api: DOWN"; FAIL=2
fi

if command -v python3 > /dev/null; then
  if python3 - <<'PY' 2>/dev/null
from pathlib import Path
p = Path("data/state/orchestration_state.sqlite")
raise SystemExit(0 if p.exists() or not any(Path("data").glob("*")) else 1)
PY
  then
    echo "[health] persistence: OK"
  else
    echo "[health] persistence: DEGRADED"; [ "$FAIL" -lt 1 ] && FAIL=1
  fi
fi

echo "[health] exit=${FAIL}"
exit "$FAIL"
