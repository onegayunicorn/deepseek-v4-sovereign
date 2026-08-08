#!/usr/bin/env bash
# build_linux.sh — build the Sovereign Linux binary + DEB package.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p dist

echo "→ PyInstaller onefile (Linux x86_64)"
.venv/bin/pip install -q pyinstaller 2>/dev/null || pip install -q pyinstaller
.venv/bin/pyinstaller --clean --noconfirm builds/exe/sovereign.spec
mv dist/sovereign dist/Sovereign-linux-x86_64 2>/dev/null || true

echo "→ DEB packaging"
DEB_DIR="dist/deb-root/opt/sovereign"
rm -rf dist/deb-root
mkdir -p "$DEB_DIR" dist/deb-root/DEBIAN
cp dist/Sovereign-linux-x86_64 "$DEB_DIR/sovereign"
cat > dist/deb-root/DEBIAN/control <<'CTRL'
Package: sovereign
Version: 0.3.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: OGU <onegayunicorn@gmail.com>
Description: Sovereign Orchestrator — photonic-DNA AI orchestration layer
CTRL
dpkg-deb --build dist/deb-root dist/Sovereign.deb
rm -rf dist/deb-root
echo "✅ Sovereign.deb → dist/"
