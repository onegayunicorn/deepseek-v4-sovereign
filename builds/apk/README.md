# Sovereign — Android APK (free-roaming companion)

Buildable Android app for your Samsung device: dashboard shell + **free-roaming
AI companion** with a floating **bubble** (chat head) and a home-screen
**widget**.

| Feature | File |
| :--- | :--- |
| Dashboard (WebView shell) | `app/src/main/java/ai/sovereign/orchestrator/MainActivity.kt` |
| Bubble chat head (overlay service) | `app/src/main/java/ai/sovereign/orchestrator/BubbleService.kt` |
| Roaming client (polls orchestrator) | `app/src/main/java/ai/sovereign/orchestrator/RoamingAgentClient.kt` |
| Home-screen widget | `app/src/main/java/ai/sovereign/orchestrator/SovereignWidget.kt` |

## What it does

- **Bubble**: floating ◉ chat head over any app (SYSTEM_ALERT_WINDOW). Tap to
  expand a chat panel — talk to your orchestrator, or read proactive messages
  (fidelity drift, BCI lock, tuning-loop updates) that the companion surfaces
  unprompted. The companion runs as a foreground service (persistent).
- **Widget**: home-screen tile showing last-known fidelity / pairs / BCI,
  tap to open the dashboard.
- **Roaming loop**: polls the orchestrator every 15 s
  (`/api/v1/pero/state`, `/api/v1/telemetry`), refreshes the widget, and
  raises a notification when the system needs attention.

## Build

Requires Android SDK (compileSdk 34, minSdk 26, Java 17).

```bash
cd builds/apk
./gradlew assembleDebug          # or assembleRelease (see signing below)
# output: app/build/outputs/apk/debug/app-debug.apk
```

CI: `.github/workflows/build-binaries.yml` builds and attaches the APK on
every push/release.

### Signing

Debug builds are auto-signed with the debug key (fine for sideloading on your
own device). For release builds, configure a keystore:

```kotlin
// app/build.gradle.kts
signingConfigs {
    create("release") {
        storeFile = file("sovereign.jks")
        storePassword = System.getenv("KS_PASS") ?: ""
        keyAlias = System.getenv("KS_ALIAS") ?: "sovereign"
        keyPassword = System.getenv("KS_PASS") ?: ""
    }
}
buildTypes { release { signingConfig = signingConfigs.getByName("release") } }
```

## Install on your Samsung

1. **Orchestrator backend on the phone** (no PC needed):
   - Install [Termux](https://termux.com) from F-Droid
   - `bash <(curl -s https://raw.githubusercontent.com/onegayunicorn/deepseek-v4-sovereign/main/scripts/install-termux.sh)`
   - `sovereign dashboard` → API on `http://127.0.0.1:8000`
   (Or run the orchestrator on any LAN machine and set the URL below.)
2. **App**: copy `app-debug.apk` to the phone → allow "install unknown apps" →
   open it. Grant **overlay permission** (menu → *Grant overlay permission*)
   and **notifications** when prompted.
3. **Pair**: menu → *Start bubble companion*. The bubble appears; the roaming
   loop connects to `http://127.0.0.1:8000` (default). For a remote
   orchestrator, set `sovereign_telemetry/orchestrator_url` in the app's
   SharedPreferences (or change `RoamingAgentClient.DEFAULT_URL`).
4. **Widget**: long-press home screen → Widgets → Sovereign → add.

## Permissions

- `SYSTEM_ALERT_WINDOW` — floating bubble
- `FOREGROUND_SERVICE` (+ `specialUse`) — persistent companion loop
- `POST_NOTIFICATIONS` — proactive messages
- `INTERNET` — orchestrator API
- Bluetooth — Sovereign Ring/Buds pairing (unchanged)
