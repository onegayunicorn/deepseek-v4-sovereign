#!/usr/bin/env bash
# SOVEREIGN — backup state, memory, and artifacts
# Usage: bash scripts/backup.sh [--target state|memory|artifacts|all] [--out DIR]
set -euo pipefail
cd "$(dirname "$0")/.."

TARGET="${1:-all}"
OUT="${OUT:-data/state/backups}"
STAMP="$(date +%Y%m%d-%H%M%S)"
DEST="${OUT}/${STAMP}"

mkdir -p "$DEST"

backup_dir() {
  local name="$1" src="$2"
  if [ -d "$src" ]; then
    tar -czf "${DEST}/${name}.tar.gz" -C "$(dirname "$src")" "$(basename "$src")"
    echo "[backup] ${name}.tar.gz ($(du -h "${DEST}/${name}.tar.gz" | cut -f1))"
  fi
}

case "$TARGET" in
  state)     backup_dir state data/state ;;
  memory)    backup_dir memory data/memory ;;
  artifacts) backup_dir artifacts data/artifacts ;;
  all)
    backup_dir state data/state
    backup_dir memory data/memory
    backup_dir artifacts data/artifacts
    ;;
  *) echo "unknown target: $TARGET (state|memory|artifacts|all)" >&2; exit 2 ;;
esac

sha256sum "${DEST}"/*.tar.gz > "${DEST}/SHA256SUMS" 2>/dev/null || true
echo "[backup] complete → ${DEST}"
