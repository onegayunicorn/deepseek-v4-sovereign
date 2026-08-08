#!/usr/bin/env bash
# build_web.sh — package the static site (site/) for Pages/WASM hosting.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p dist
tar -czf dist/sovereign-web.tar.gz -C site .
echo "✅ sovereign-web.tar.gz → dist/ (site/ content)"
