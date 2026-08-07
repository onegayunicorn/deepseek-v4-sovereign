# Sovereign — Android APK Build

Builds the SOVEREIGN orchestrator shell as an Android APK: a dark-themed
WebView (`#0A0A10` background, `#00E5FF` cyan accent) that loads the
Sovereign Orchestrator dashboard.

## Prerequisites

- **JDK 17** (Temurin/OpenJDK). Set `JAVA_HOME` or ensure `java` is on `PATH`.
- **Android SDK** — set `ANDROID_HOME` (e.g. `/opt/android-sdk`). Gradle
  downloads the required SDK components (platform 34, build-tools) on first
  build.
- **Gradle 8.2+** on `PATH`, or a generated Gradle wrapper (`gradle wrapper`
  produces `./gradlew`). The build script falls back to the wrapper when
  present, otherwise to system `gradle`.

## Build

```bash
cd builds/apk

# Debug APK (default)
./build_apk.sh

# Release APK
RELEASE=1 ./build_apk.sh
```

Manual equivalent:

```bash
cd builds/apk
./gradlew :app:assembleDebug      # or :app:assembleRelease
```

## Output

| Variant  | Path                                                    |
|----------|---------------------------------------------------------|
| Debug    | `app/build/outputs/apk/debug/app-debug.apk`             |
| Release  | `app/build/outputs/apk/release/app-release.apk`         |

## Signing

Debug builds are signed automatically with the debug keystore
(`~/.android/debug.keystore`). Release builds are signed with the same debug
key by default — **do not ship that**.

Production signing:

1. Create a keystore:

   ```bash
   keytool -genkeypair -v -keystore sovereign-release.keystore \
     -alias sovereign -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Wire `signingConfigs` in `app/build.gradle.kts`:

   ```kotlin
   signingConfigs {
       create("release") {
           storeFile = file("../sovereign-release.keystore")
           storePassword = System.getenv("SOVEREIGN_STORE_PASSWORD")
           keyAlias = "sovereign"
           keyPassword = System.getenv("SOVEREIGN_KEY_PASSWORD")
       }
   }
   ```

3. Verify the signature with `apksigner` (Android SDK build-tools):

   ```bash
   $ANDROID_HOME/build-tools/34.0.0/apksigner verify --print-certs \
     app/build/outputs/apk/release/app-release.apk
   ```

Keep the keystore and passwords out of version control.
