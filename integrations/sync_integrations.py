#!/usr/bin/env python3
"""Sync all 18 OGU projects as pinned git submodules.

One command → entire constellation cloned at known-good commits.
Usage:
    python integrations/sync_integrations.py status   (read-only, default)
    python integrations/sync_integrations.py init
    python integrations/sync_integrations.py pin
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

OGU_PROJECTS = {
    "mocking-jay": "https://github.com/onegayunicorn/mocking-jay.git",
    "core": "https://github.com/onegayunicorn/core.git",
    "photonic-entanglement-engine": "https://github.com/onegayunicorn/photonic-entanglement-research-orchestrator.git",
    "dna-unfolding-lab": "https://github.com/onegayunicorn/dna-unfolding-lab.git",
    "codality": "https://github.com/onegayunicorn/codality.git",
    "universal-driver": "https://github.com/onegayunicorn/universal-driver.git",
    "drivers": "https://github.com/onegayunicorn/drivers.git",
    "sensors": "https://github.com/onegayunicorn/sensors.git",
    "pipelines": "https://github.com/onegayunicorn/pipelines.git",
    "buckets": "https://github.com/onegayunicorn/buckets.git",
    "kaleidoscope": "https://github.com/onegayunicorn/kaleidoscope.git",
    "moodchroma": "https://github.com/onegayunicorn/moodchroma.git",
    "optogenetics": "https://github.com/onegayunicorn/optogenetics.git",
    "skills": "https://github.com/onegayunicorn/skills.git",
    "website": "https://github.com/onegayunicorn/website.git",
    "onegayunicorn": "https://github.com/onegayunicorn/onegayunicorn.git",
    "ogu-build": "https://github.com/onegayunicorn/ogu-build.git",
    "deepseek-v4-sovereign": "https://github.com/onegayunicorn/deepseek-v4-sovereign.git",
}

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "external"


def run(*a, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(a, check=True, cwd=str(ROOT), **kw)


def init_all() -> None:
    EXT.mkdir(exist_ok=True)
    for name, url in OGU_PROJECTS.items():
        p = EXT / name
        if not p.exists():
            run("git", "submodule", "add", url, f"external/{name}")
    run("git", "submodule", "update", "--init", "--recursive")


def pin_all() -> None:
    for name in OGU_PROJECTS:
        p = EXT / name
        if p.exists():
            h = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(p)).decode().strip()
            print(f"{name}: {h[:10]}")


def status() -> None:
    for name in OGU_PROJECTS:
        p = EXT / name
        mark = "✅" if p.exists() else "⬜"
        print(f"{mark} {name}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"init": init_all, "pin": pin_all, "status": status}.get(cmd, status)()
