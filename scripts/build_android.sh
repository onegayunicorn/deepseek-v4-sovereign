#!/usr/bin/env bash
# build_android.sh — build the Sovereign APK (wrapper around builds/apk).
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p dist
bash builds/apk/build_apk.sh "$@"
APK=$(ls builds/apk/app/build/outputs/apk/release/*.apk 2>/dev/null | head -1 || true)
[ -z "$APK" ] && APK=$(ls builds/apk/app/build/outputs/apk/debug/*.apk 2>/dev/null | head -1 || true)
if [ -n "$APK" ]; then
  cp "$APK" dist/Sovereign.apk
  echo "✅ APK → dist/Sovereign.apk"
else
  echo "⚠️  APK build produced no output" >&2
  exit 1
fi
