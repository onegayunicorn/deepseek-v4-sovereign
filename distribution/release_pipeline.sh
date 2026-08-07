#!/usr/bin/env bash
#
# release_pipeline.sh — SOVEREIGN end-to-end release orchestration.
#
# Usage:
#   VERSION=0.2.0 CHANNELS=github-releases,apk-direct,docker-hub \
#     distribution/release_pipeline.sh
#
# Environment:
#   VERSION   (required) semantic version, e.g. 0.2.0
#   CHANNELS  (required) comma-separated channel keys from
#             distribution/release_channels.yaml
#
# The pipeline: bumps the version -> builds APK + EXE -> signs (echoed) ->
# generates checksums -> echoes per-channel publish commands -> summary.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$REPO_ROOT/distribution"
BUILDS_DIR="$REPO_ROOT/builds"
CHANNEL_FILE="$DIST_DIR/release_channels.yaml"

VERSION="${VERSION:?VERSION env var is required, e.g. VERSION=0.2.0}"
CHANNELS="${CHANNELS:?CHANNELS env var is required, e.g. CHANNELS=github-releases,docker-hub}"

IFS=',' read -r -a CHANNEL_LIST <<<"$CHANNELS"
if [[ ${#CHANNEL_LIST[@]} -eq 0 ]]; then
    echo "ERROR: CHANNELS is empty." >&2
    exit 1
fi

step() {
    echo ""
    echo "================================================================================"
    echo "  [$1] $2"
    echo "================================================================================"
}

# --- 1. Version bump ---------------------------------------------------------
step "1/7" "Version bump -> $VERSION"
if [[ -f "$REPO_ROOT/pyproject.toml" ]]; then
    sed -i -E "s/^(version = \")[0-9]+\.[0-9]+\.[0-9]+(\")/\1$VERSION\2/" \
        "$REPO_ROOT/pyproject.toml"
    grep -n "^version" "$REPO_ROOT/pyproject.toml"
else
    echo "WARN: pyproject.toml not found at repo root; skipping version bump." >&2
fi
echo "[sovereign] version bumped to $VERSION"

# --- 2. Changelog -------------------------------------------------------------
step "2/7" "Changelog"
if [[ -f "$REPO_ROOT/CHANGELOG.md" ]]; then
    echo "[sovereign] CHANGELOG.md found — add an entry for v$VERSION if missing."
else
    echo "WARN: CHANGELOG.md not found; create one before publishing." >&2
fi

# --- 3. Build (APK + EXE) -----------------------------------------------------
step "3/7" "Build artifacts"
echo "[sovereign] Building release APK..."
RELEASE=1 "$BUILDS_DIR/apk/build_apk.sh"
echo "[sovereign] Building EXE (Windows instructions + Linux fallback)..."
"$BUILDS_DIR/exe/build_exe.sh"

APK="$BUILDS_DIR/apk/app/build/outputs/apk/release/app-release.apk"
EXE="$BUILDS_DIR/exe/dist/sovereign.exe"
[[ -f "$APK" ]] || echo "WARN: release APK not found: $APK" >&2
[[ -f "$EXE" ]] || echo "WARN: Windows EXE not found: $EXE (build on Windows)" >&2

# --- 4. Sign (echoed — run on the appropriate signing host) -------------------
step "4/7" "Sign artifacts"
echo "[sovereign] APK signing (Android SDK build-tools):"
echo "  apksigner sign --ks sovereign-release.keystore --ks-key-alias sovereign \\"
echo "    --ks-pass env:SOVEREIGN_STORE_PASSWORD --key-pass env:SOVEREIGN_KEY_PASSWORD \\"
echo "    $APK"
echo ""
echo "[sovereign] EXE signing (Windows host, signtool):"
echo "  signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 \\"
echo "    /f sovereign-cert.pfx /p \$PFX_PASSWORD \\"
echo "    /d \"Sovereign Orchestrator\" /du https://sovereign.ai $EXE"

# --- 5. Checksums -------------------------------------------------------------
step "5/7" "Integrity checksums"
mkdir -p "$DIST_DIR/checksums"
SUM_FILE="$DIST_DIR/checksums/sha256sums-v$VERSION.txt"
: >"$SUM_FILE"
for artifact in "$APK" "$EXE" "$BUILDS_DIR/exe/dist/sovereign"; do
    if [[ -f "$artifact" ]]; then
        sha256sum "$artifact" >>"$SUM_FILE"
        echo "[sovereign] checksummed: $artifact"
    fi
done
echo "[sovereign] checksums written to $SUM_FILE"

# --- 6. Publish per channel (echoed commands) ---------------------------------
step "6/7" "Publish (dry-run — commands echoed, not executed)"
if [[ ! -f "$CHANNEL_FILE" ]]; then
    echo "ERROR: $CHANNEL_FILE not found." >&2
    exit 1
fi
for channel in "${CHANNEL_LIST[@]}"; do
    echo ""
    echo "----------------------------------------"
    echo "[sovereign] Channel: $channel"
    echo "----------------------------------------"
    # Substituted commands for this channel, read from release_channels.yaml.
    # {VERSION} placeholders are replaced here. awk extracts the block from
    # the channel header until the next top-level channel key.
    awk -v ch="$channel" '
        $0 == "  " ch ":" { in_block = 1; next }
        in_block && /^  [a-z0-9-]+:/ { exit }
        in_block { print }
    ' "$CHANNEL_FILE" | sed "s/{VERSION}/$VERSION/g" | sed -e 's/^/  /'
    if ! grep -q "^  $channel:" "$CHANNEL_FILE"; then
        echo "  WARN: channel '$channel' not found in $CHANNEL_FILE" >&2
    fi
done

# --- 7. Summary ---------------------------------------------------------------
step "7/7" "Summary"
echo "  Version      : $VERSION"
echo "  Channels     : ${CHANNEL_LIST[*]}"
echo "  Artifacts    : $APK / $EXE"
echo "  Checksums    : $SUM_FILE"
echo ""
echo "[sovereign] Release pipeline finished (dry-run). Run signing and publish"
echo "[sovereign] commands on the appropriate hosts, then smoke-test."
