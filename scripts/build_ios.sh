#!/usr/bin/env bash
# build_ios.sh — build the Sovereign iOS app (requires macOS + Xcode CI).
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p dist
bash builds/ios/build_ios.sh "$@"
if [ -f builds/ios/build/Sovereign.ipa ]; then
  cp builds/ios/build/Sovereign.ipa dist/Sovereign.ipa
  echo "✅ IPA → dist/Sovereign.ipa"
else
  echo "⚠️  iOS build produced no IPA (macOS only — see CI macos-14 job)" >&2
  exit 1
fi
