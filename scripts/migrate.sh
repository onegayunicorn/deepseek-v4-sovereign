#!/usr/bin/env bash
# SOVEREIGN — apply schema migrations to state/memory databases
# Migration scripts live in data/state/migrations/*.sql (applied in order).
set -euo pipefail
cd "$(dirname "$0")/.."

MIGRATIONS_DIR="data/state/migrations"
DBS=("data/state/orchestration_state.sqlite" "data/memory/episodic/episodes.db" "data/memory/semantic/facts.db")

mkdir -p "$MIGRATIONS_DIR"

for db in "${DBS[@]}"; do
  [ -f "$db" ] || { echo "[migrate] skip ${db} (not created yet)"; continue; }
  for sql in "$MIGRATIONS_DIR"/*.sql; do
    [ -f "$sql" ] || continue
    echo "[migrate] applying $(basename "$sql") → $db"
    sqlite3 "$db" < "$sql" 2>/dev/null || echo "[migrate] sqlite3 unavailable or failed (install sqlite3)"
  done
  echo "[migrate] ${db} done"
done

echo "[migrate] complete"
