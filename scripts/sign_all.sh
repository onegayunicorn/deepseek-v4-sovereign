#!/usr/bin/env bash
# sign_all.sh — best-effort signing of every produced binary.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p dist

for a in dist/Sovereign.apk; do
  [ -f "$a" ] && bash scripts/sign_apk.sh "$a" || true
done
for e in dist/Sovereign.exe dist/Sovereign-linux-x86_64; do
  [ -f "$e" ] && bash scripts/sign_exe.sh "$e" || true
done
echo "signing pass complete (skipped where tooling/certs are absent)"
