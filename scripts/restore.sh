#!/usr/bin/env bash
# SOVEREIGN — restore from a backup snapshot
# Usage: bash scripts/restore.sh --snapshot <dir> [--target state|memory|artifacts|all]
set -euo pipefail
cd "$(dirname "$0")/.."

SNAPSHOT="${SNAPSHOT:-}"
TARGET="${TARGET:-all}"
while [ $# -gt 0 ]; do
  case "$1" in
    --snapshot) SNAPSHOT="$2"; shift 2 ;;
    --target)   TARGET="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[ -n "$SNAPSHOT" ] || { echo "usage: restore.sh --snapshot <dir>" >&2; exit 2; }
[ -d "$SNAPSHOT" ] || { echo "snapshot dir not found: $SNAPSHOT" >&2; exit 2; }

restore_dir() {
  local name="$1" dest="$2"
  local archive="${SNAPSHOT}/${name}.tar.gz"
  [ -f "$archive" ] || { echo "[restore] skip ${name} (no archive)"; return; }
  mkdir -p "$dest"
  tar -xzf "$archive" -C "$dest"
  echo "[restore] ${name} → ${dest}"
}

case "$TARGET" in
  state)     restore_dir state data ;;
  memory)    restore_dir memory data ;;
  artifacts) restore_dir artifacts data ;;
  all)
    restore_dir state data
    restore_dir memory data
    restore_dir artifacts data
    ;;
esac

echo "[restore] complete — restart the orchestrator"
