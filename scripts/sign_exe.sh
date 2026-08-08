#!/usr/bin/env bash
# sign_exe.sh — Authenticode-sign the Sovereign EXE (best-effort, Windows CI).
set -euo pipefail
EXE="${1:-dist/Sovereign.exe}"
[ -f "$EXE" ] || { echo "⚠️  $EXE not found — signing skipped"; exit 0; }
command -v signtool >/dev/null 2>&1 || { echo "⚠️  signtool not found — signing skipped"; exit 0; }
signtool sign /fd SHA256 /f "${SIGN_CERT:-cert.pfx}" \
  /p "${SIGN_PASS:-}" "$EXE" 2>/dev/null || echo "⚠️  signing failed (no cert?)"
