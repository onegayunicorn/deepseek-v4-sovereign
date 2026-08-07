# Sovereign — Packaging Guide

Options for packaging and distributing the SOVEREIGN orchestrator
(FastAPI API + CLI, import root `sovereign`, brand palette
`#0A0A10` / `#00E5FF` / `#00FFCC`).

## 1. PyInstaller onefile (CLI / desktop)

- **Where**: `builds/exe/sovereign.spec` + `build_exe.ps1` / `build_exe.sh`.
- **What**: single `sovereign.exe` (Windows) or `sovereign` (Linux) bundle
  containing Python 3.11, FastAPI, uvicorn and the `sovereign` package.
- **Trade-offs**: fast to ship, no runtime install; onefile extracts to a
  temp dir at startup (slower cold start, AV false-positive risk).
- **Tips**: keep `console=True` for the CLI; add an `.ico` to `EXE(icon=…)`;
  pin `pyinstaller` in CI; smoke-test the frozen binary in CI.

## 2. Electron wrapper (desktop dashboard)

- **What**: package the frontend dashboard (`frontend/`) as a desktop app
  with a WebView shell — the Android app already mirrors this pattern.
- **Tooling**: `electron-builder` targets NSIS (Windows), DMG (macOS), AppImage
  (Linux); auto-update via `electron-updater`.
- **Trade-offs**: heavier (~100 MB), but gives native menus, tray, offline
  caching and OS-level integration.
- **Branding**: apply the Sovereign dark palette in `BrowserWindow`
  (`backgroundColor: '#0A0A10'`, accent `#00E5FF`).

## 3. Docker images (server)

- **Where**: `docker/` (Dockerfile for the FastAPI orchestrator).
- **Build**: `docker buildx build --platform linux/amd64,linux/arm64 … --push`.
- **Run**: `docker run -p 8000:8000 sovereignai/orchestrator:0.1.0`.
- **Notes**: non-root user, read-only rootfs, healthcheck against `/health`,
  tag with `{VERSION}` and `latest`.

## 4. Windows code signing (signtool + cert)

- **Why**: unsigned EXEs trigger SmartScreen and antivirus warnings.
- **Cert**: OV/EV code-signing certificate (e.g. Sectigo, DigiCert); keep the
  `.pfx` in a secrets store, never in git.
- **Sign** (Windows SDK):

  ```powershell
  signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 \
    /f sovereign-cert.pfx /p $env:PFX_PASSWORD \
    /d "Sovereign Orchestrator" /du https://sovereign.ai \
    builds\exe\dist\sovereign.exe
  ```

- **Verify**:

  ```powershell
  signtool verify /pa /v builds\exe\dist\sovereign.exe
  ```

## 5. APK signing (apksigner)

- **Debug**: auto-signed with the debug keystore (`~/.android/debug.keystore`).
- **Release**: create a keystore with `keytool`, wire `signingConfigs` in
  `app/build.gradle.kts`, then verify:

  ```bash
  $ANDROID_HOME/build-tools/34.0.0/apksigner verify --print-certs \
    builds/apk/app/build/outputs/apk/release/app-release.apk
  ```

- **Notes**: never rotate the release key once users have the APK; store the
  keystore offline + a backup. For Play distribution, upload the AAB with
  Play App Signing instead.

## 6. macOS notarization (notes only)

- App bundles must be signed with an Apple Developer ID and notarized:
  `codesign --deep --force --options runtime`, then
  `xcrun notarytool submit … --wait`, then staple
  (`xcrun stapler staple`).
- Requires an Apple Developer account + `APPLE_ID`, `APPLE_TEAM_ID` and
  app-specific password.
- Not yet automated — see `pipeline.md` for the manual step.

## 7. Integrity checksums (sha256)

- Generate for every artifact before publishing:

  ```bash
  mkdir -p distribution/checksums
  cd builds/apk/app/build/outputs/apk/release && sha256sum app-release.apk \
    > ../../../../../../../distribution/checksums/sha256sums-v0.1.0.txt
  cd ../../../../../../../builds/exe/dist && sha256sum sovereign.exe \
    >> ../../../../../../distribution/checksums/sha256sums-v0.1.0.txt
  ```

- Publish the checksums file alongside the artifacts (GitHub release,
  `apk-direct` S3 bucket) so users can verify downloads:

  ```bash
  sha256sum -c distribution/checksums/sha256sums-v0.1.0.txt
  ```
