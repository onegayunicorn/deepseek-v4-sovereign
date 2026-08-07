#!/usr/bin/env bash
#
# build_exe.sh — cross-platform wrapper for the Sovereign EXE build.
#
# PyInstaller does NOT cross-compile: a Windows .exe must be produced on
# Windows. This script therefore:
#   1. Prints the Windows build instructions.
#   2. Falls back to building a Linux onefile binary (so CI/Unix users still
#      get a runnable artifact) unless SKIP_LINUX=1.
#
# Usage:
#   ./build_exe.sh          # print Windows instructions + build Linux binary
#   SKIP_LINUX=1 ./build_exe.sh   # instructions only
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# On a Windows shell, just delegate to the PowerShell script.
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
        echo "[sovereign] Windows shell detected — invoking build_exe.ps1"
        exec powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/build_exe.ps1"
        ;;
esac

cat <<'EOF'
[sovereign] Windows .exe build
--------------------------------
PyInstaller cannot cross-compile; the Windows .exe must be produced on a
Windows 10+ machine with Python 3.11. Run:

    cd builds/exe
    powershell -ExecutionPolicy Bypass -File build_exe.ps1

(which creates .venv, installs requirements.txt + PyInstaller, runs
`pyinstaller --clean sovereign.spec`, and prints dist\sovereign.exe)
--------------------------------
EOF

if [[ "${SKIP_LINUX:-0}" == "1" ]]; then
    echo "[sovereign] SKIP_LINUX=1 — no Linux fallback binary built."
    exit 0
fi

echo "[sovereign] Falling back to a Linux onefile binary..."

VENV_DIR="$SCRIPT_DIR/.venv-linux"
if [[ ! -d "$VENV_DIR" ]]; then
    python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/pip" install --upgrade pip >/dev/null
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/../../../requirements.txt" pyinstaller >/dev/null
"$VENV_DIR/bin/pyinstaller" --clean --noconfirm "$SCRIPT_DIR/sovereign.spec"

BIN="$SCRIPT_DIR/dist/sovereign"
if [[ ! -f "$BIN" ]]; then
    echo "ERROR: Linux binary not found at $BIN" >&2
    exit 1
fi
echo ""
echo "[sovereign] BUILD OK"
echo "[sovereign] Linux binary: $BIN"
ls -lh "$BIN"
