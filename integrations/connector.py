#!/usr/bin/env python3
"""SOVEREIGN — integration connector.

Discovers and validates every connected OGU project listed in
integrations/registry.yaml (siblings of the monorepo, one level up).
Prints a connection status report; used by `make status`.

Usage:
    python3 integrations/connector.py [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_MONOREPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_MONOREPO))
sys.path.insert(0, str(_MONOREPO / "src"))

from sovereign.utils.serialization import load_yaml  # noqa: E402

REGISTRY = _MONOREPO / "integrations" / "registry.yaml"


def discover() -> dict:
    registry = load_yaml(REGISTRY)
    root = (_MONOREPO / registry.get("workspace_root", "..")).resolve()

    status: dict = {"root": str(root), "projects": [], "connected": 0, "missing": 0}
    for entry in registry.get("projects", []):
        target = (root / entry["path"].removeprefix("../")).resolve()
        exists = target.is_dir()
        surface = []
        if exists:
            for item in entry.get("surface", []):
                surface.append({"name": item, "exists": (target / item).exists() or (target / f"{item}.py").exists()})
        record = {
            "id": entry["id"],
            "path": entry["path"],
            "role": entry.get("role"),
            "connected": exists,
            "surface": surface,
            "flagship": entry["id"] in registry.get("flagships", []),
        }
        status["projects"].append(record)
        status["connected" if exists else "missing"] += 1

    # Adapter coverage check.
    adapters = sorted((_MONOREPO / "integrations" / "projects").glob("*.md"))
    status["adapter_files"] = [a.name for a in adapters]
    status["adapter_missing"] = [
        p["id"] for p in status["projects"]
        if not (_MONOREPO / "integrations" / "projects" / f"{p['id']}.md").exists()
    ]
    return status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    status = discover()
    if args.json:
        print(json.dumps(status, indent=2))
        return 0

    print(f"SOVEREIGN integration connector — root: {status['root']}")
    print(f"connected: {status['connected']}  missing: {status['missing']}  adapters: {len(status['adapter_files'])}")
    for project in status["projects"]:
        mark = "✔" if project["connected"] else "✘"
        flag = " ★" if project["flagship"] else ""
        missing = [s["name"] for s in project["surface"] if not s["exists"]]
        detail = f"  missing surface: {missing}" if missing else ""
        print(f"  {mark} {project['id']:<32} {project['role'] or '':<12}{flag}{detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
