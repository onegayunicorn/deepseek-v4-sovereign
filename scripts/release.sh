#!/usr/bin/env bash
# Cut a full Sovereign release
# Usage: ./scripts/release.sh v0.2.0
set -euo pipefail
VERSION="${1:?usage: release.sh v0.2.0}"

echo "Cutting Sovereign $VERSION"
mkdir -p dist
bash scripts/build_android.sh || echo "⚠ android build skipped"
bash scripts/build_ios.sh || echo "⚠ iOS skipped (needs macOS)"
bash scripts/build_windows.sh || echo "⚠ Windows skipped"
bash scripts/build_linux.sh
bash scripts/build_web.sh
bash scripts/sign_all.sh || echo "⚠ signing skipped"

git tag -a "$VERSION" -m "Sovereign $VERSION"
git push origin "$VERSION"
gh release create "$VERSION" \
  --title "Sovereign $VERSION" \
  --notes-file CHANGELOG.md \
  dist/Sovereign.apk dist/Sovereign.exe dist/Sovereign.deb site/sovereign-wasm.tar.gz

echo "🎉 Release $VERSION published"
