#!/usr/bin/env bash
#
# build_ios.sh — Sovereign iOS build (requires macOS + Xcode).
#
# The Python core is packaged via `kivy-ios` (or pybee/briefcase) and the
# native Swift shell wraps the FastAPI orchestrator. This script prepares
# the Xcode project and runs xcodebuild.
#
# Usage:
#   ./build_ios.sh                 # simulator build
#   RELEASE=1 ./build_ios.sh       # device (signing) build
#
# Prerequisites:
#   - macOS with Xcode 15+ (xcodebuild on PATH)
#   - Python 3.11 (python3 on PATH)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[sovereign] iOS build requires macOS + Xcode."
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "ERROR: iOS builds must run on macOS (xcodebuild unavailable here)." >&2
    echo "       CI uses macos-14 runners; see .github/workflows/packages.yml." >&2
    exit 1
fi

# --- 1. Bootstrap the Python side (kivy-ios toolchain) ----------------------
if [[ ! -d .venv-ios ]]; then
    python3 -m venv .venv-ios
fi
.venv-ios/bin/pip install --upgrade pip >/dev/null
.venv-ios/bin/pip install -r ../../requirements.txt kivy-ios >/dev/null

# --- 2. Create the Xcode project --------------------------------------------
if [[ ! -d "ios/Sovereign.xcodeproj" ]]; then
    echo "[sovereign] Generating Xcode project (sovereign/ios)..."
    .venv-ios/bin/toolchain create sovereign ios 2>/dev/null || true
fi

# --- 3. Build ----------------------------------------------------------------
CONFIG="Debug"
DEST="generic/platform=iOS Simulator"
if [[ "${RELEASE:-0}" == "1" ]]; then
    CONFIG="Release"
    DEST="generic/platform=iOS"
fi

xcodebuild \
    -project ios/Sovereign.xcodeproj \
    -scheme Sovereign \
    -configuration "$CONFIG" \
    -destination "$DEST" \
    build

echo ""
echo "[sovereign] iOS BUILD OK — see ios/build for the .app bundle."
