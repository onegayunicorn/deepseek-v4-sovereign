#!/usr/bin/env bash
#
# build_apk.sh — build the Sovereign Android APK.
#
# Usage:
#   ./build_apk.sh             # debug APK (app/build/outputs/apk/debug)
#   RELEASE=1 ./build_apk.sh   # release APK (app/build/outputs/apk/release)
#
# Prerequisites:
#   - JDK 17 (JAVA_HOME set, or `java` on PATH)
#   - Android SDK (ANDROID_HOME) and either the Gradle wrapper or `gradle`
#
# Output:
#   prints the path of the produced APK.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

TASK=":app:assembleDebug"
VARIANT="debug"
if [[ "${RELEASE:-0}" == "1" ]]; then
    TASK=":app:assembleRelease"
    VARIANT="release"
    echo "[sovereign] Building RELEASE APK ($TASK)"
else
    echo "[sovereign] Building DEBUG APK ($TASK)"
fi

# --- 1. Locate the JDK (17) ------------------------------------------------
if [[ -n "${JAVA_HOME:-}" && -x "$JAVA_HOME/bin/java" ]]; then
    echo "[sovereign] Using JAVA_HOME=$JAVA_HOME"
    export PATH="$JAVA_HOME/bin:$PATH"
elif command -v java >/dev/null 2>&1; then
    echo "[sovereign] Using java from PATH: $(command -v java)"
else
    echo "ERROR: JDK 17 not found. Set JAVA_HOME or install a JDK (e.g. Temurin 17)." >&2
    exit 1
fi
java -version >/dev/null 2>&1 || { echo "ERROR: 'java' did not run correctly." >&2; exit 1; }

# --- 2. Resolve the Gradle launcher ----------------------------------------
GRADLE_CMD=(./gradlew)
if [[ ! -x "./gradlew" ]]; then
    if command -v gradle >/dev/null 2>&1; then
        echo "[sovereign] ./gradlew not found — falling back to system 'gradle'."
        GRADLE_CMD=(gradle)
    else
        echo "ERROR: ./gradlew is missing and 'gradle' is not on PATH." >&2
        echo "       Generate the wrapper (gradle wrapper) or install Gradle 8.2+." >&2
        exit 1
    fi
fi

# --- 3. Warn about a missing Android SDK ------------------------------------
if [[ -z "${ANDROID_HOME:-}" && -z "${ANDROID_SDK_ROOT:-}" ]]; then
    echo "WARN: ANDROID_HOME not set; Gradle will look for the SDK via local.properties." >&2
fi

# --- 4. Build ----------------------------------------------------------------
"${GRADLE_CMD[@]}" "$TASK"

# --- 5. Report the artifact --------------------------------------------------
APK_PATH="$SCRIPT_DIR/app/build/outputs/apk/$VARIANT/app-$VARIANT.apk"
if [[ -f "$APK_PATH" ]]; then
    echo ""
    echo "[sovereign] BUILD OK"
    echo "[sovereign] APK: $APK_PATH"
    ls -lh "$APK_PATH"
else
    echo "ERROR: expected APK not found at $APK_PATH" >&2
    exit 1
fi
