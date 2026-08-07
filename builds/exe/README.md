# Sovereign — Windows EXE Build

Produces a onefile Windows executable (`sovereign.exe`) for the SOVEREIGN
CLI/orchestrator using PyInstaller.

## Prerequisites

- **Windows 10+** (PyInstaller does not cross-compile — the `.exe` must be
  built on Windows; see `build_exe.sh` for the Linux fallback).
- **Python 3.11** from [python.org](https://python.org) with `python` on PATH.
- Network access to PyPI for dependency installs.

## Build

From PowerShell in this directory:

```powershell
.\build_exe.ps1
```

The script:

1. Creates a local virtual environment (`.venv`).
2. Installs `requirements.txt` + PyInstaller.
3. Runs `pyinstaller --clean --noconfirm sovereign.spec`.
4. Prints the path of the produced executable.

Or from a Unix/CI host (prints Windows instructions, then builds a Linux
onefile binary as a fallback):

```bash
./build_exe.sh            # instructions + Linux binary
SKIP_LINUX=1 ./build_exe.sh
```

## Output

| Platform | Path                                    |
|----------|-----------------------------------------|
| Windows  | `builds/exe/dist/sovereign.exe`         |
| Linux    | `builds/exe/dist/sovereign`             |

## Smoke test

```powershell
.\dist\sovereign.exe --help
.\dist\sovereign.exe dashboard --port 8000
```

## Notes

- `console=True` is set in `sovereign.spec` because this is a CLI tool.
- `upx=True` compresses the bundle if UPX is on PATH (optional).
- For distribution, sign the `.exe` (see
  `distribution/packaging/README.md` — Windows code signing with
  `signtool`).
