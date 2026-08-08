#!/usr/bin/env bash
# build_windows.sh — build the Sovereign Windows EXE (Windows CI only).
# Runs build_exe.ps1 via PowerShell when on Windows; on other platforms
# prints a pointer to the CI job that builds it.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p dist

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    powershell -ExecutionPolicy Bypass -File builds/exe/build_exe.ps1
    [ -f dist/Sovereign.exe ] && echo "✅ EXE → dist/Sovereign.exe" || { echo "⚠️  build failed" >&2; exit 1; }
    ;;
  *)
    echo "⚠️  Windows EXE builds run on the windows-latest CI job (.github/workflows/build-binaries.yml)." >&2
    exit 0
    ;;
esac
