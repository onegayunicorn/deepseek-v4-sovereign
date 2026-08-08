#!/usr/bin/env bash
# sign_apk.sh — sign the Sovereign APK (best-effort, requires keystore).
# Usage: KS_PASS=... KS_ALIAS=... ./scripts/sign_apk.sh path/to/app.apk [keystore.jks]
set -euo pipefail
APK="${1:?usage: sign_apk.sh app.apk [keystore]}"
KS="${2:-deploy/android/keystore.jks}"
[ -n "${KS_PASS:-}" ] || { echo "⚠️  KS_PASS unset — signing skipped"; exit 0; }

if command -v apksigner >/dev/null 2>&1; then
  apksigner sign --ks "$KS" --ks-pass "pass:${KS_PASS}" \
    --ks-key-alias "${KS_ALIAS:-sovereign}" --out "${APK%.apk}-signed.apk" "$APK"
  mv "${APK%.apk}-signed.apk" "$APK"
  echo "✅ signed: $APK"
else
  echo "⚠️  apksigner not found — signing skipped (CI installs build-tools)"
fi
