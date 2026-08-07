# build_exe.ps1 — Build the Sovereign Windows onefile executable.
#
# Usage (from builds/exe/):
#   .\build_exe.ps1
#
# Steps:
#   1. Create a local virtual environment (.venv)
#   2. Install runtime deps (requirements.txt) + PyInstaller
#   3. Run `pyinstaller --clean sovereign.spec`
#   4. Print the output executable path
#
# Prerequisites: Python 3.11 on PATH, Windows 10+.
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ExeDir = $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $ExeDir "..\..\..")).Path

Write-Host "[sovereign] Repo root : $RepoRoot"
Write-Host "[sovereign] Build dir : $ExeDir"

# --- 1. Python + venv ------------------------------------------------------
$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    throw "python not found on PATH. Install Python 3.11 from python.org and re-run."
}

$VenvDir = Join-Path $ExeDir ".venv"
if (-not (Test-Path $VenvDir)) {
    Write-Host "[sovereign] Creating virtual environment at $VenvDir"
    & python -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) { throw "Failed to create virtual environment." }
}

$Pip = Join-Path $VenvDir "Scripts\pip.exe"
$PyInstaller = Join-Path $VenvDir "Scripts\pyinstaller.exe"

# --- 2. Dependencies --------------------------------------------------------
Write-Host "[sovereign] Installing runtime dependencies + PyInstaller..."
& $Pip install --upgrade pip
& $Pip install -r (Join-Path $RepoRoot "requirements.txt") pyinstaller
if ($LASTEXITCODE -ne 0) { throw "pip install failed." }

# --- 3. Build ----------------------------------------------------------------
Write-Host "[sovereign] Running PyInstaller (sovereign.spec)..."
Push-Location $ExeDir
try {
    & $PyInstaller --clean --noconfirm (Join-Path $ExeDir "sovereign.spec")
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE." }
} finally {
    Pop-Location
}

# --- 4. Report ---------------------------------------------------------------
$OutExe = Join-Path $ExeDir "dist\sovereign.exe"
if (-not (Test-Path $OutExe)) {
    throw "Build finished but $OutExe was not produced."
}
$Size = (Get-Item $OutExe).Length
Write-Host ""
Write-Host "[sovereign] BUILD OK"
Write-Host "[sovereign] Executable: $OutExe"
Write-Host ("[sovereign] Size      : {0:N0} bytes" -f $Size)
