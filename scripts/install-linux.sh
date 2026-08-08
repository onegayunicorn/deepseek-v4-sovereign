#!/usr/bin/env bash
# One-line installer — Linux
set -euo pipefail
VERSION="${1:-latest}"
PREFIX="${SOVEREIGN_PREFIX:-$HOME/.sovereign}"

echo "Installing Sovereign $VERSION → $PREFIX"
mkdir -p "$PREFIX/bin" "$PREFIX/data" "$PREFIX/models"

if command -v curl >/dev/null; then DL="curl -fsSL"; else DL="wget -qO-"; fi
$DL "https://github.com/onegayunicorn/deepseek-v4-sovereign/releases/$VERSION/download/Sovereign.deb" -o /tmp/sovereign.deb 2>/dev/null || true

if [ -f /tmp/sovereign.deb ] && command -v dpkg >/dev/null; then
  sudo dpkg -i /tmp/sovereign.deb || sudo apt-get install -fy
else
  python3 -m pip install --user -e "git+https://github.com/onegayunicorn/deepseek-v4-sovereign@main#egg=sovereign"
fi

ln -sf "$(command -v sovereign 2>/dev/null || true)" "$PREFIX/bin/sovereign" 2>/dev/null || true

echo ""
echo "✅ Sovereign installed. Run: sovereign dashboard"
