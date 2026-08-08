#!/usr/bin/env python3
"""Verify all registry YAML files and their cross-references.

Checks:
1. Every registry entry's ``file`` exists.
2. Trigger files reference real task ids.
3. Workflow steps reference real task/action ids; triggers resolve.
4. Agent files' implementation modules are importable.
"""

from __future__ import annotations

import glob
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)


def load(p: str) -> dict:
    with open(p) as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    errors: list[str] = []

    # 1. registry file refs resolve
    for reg in [
        "triggers/registry.yaml",
        "actions/registry.yaml",
        "tasks/registry.yaml",
        "agents/registry.yaml",
        "routines/registry.yaml",
        "operations/registry.yaml",
        "workflows/registry.yaml",
        "modules/registry.yaml",
    ]:
        d = load(reg)
        key = [k for k in d if k != "version"]
        if not key:
            continue
        for entry in d[key[0]]:
            f = entry.get("file")
            if f and not os.path.exists(os.path.join(os.path.dirname(reg), f)):
                errors.append(f"{reg}: missing file {f}")

    # 2. trigger files reference real task ids
    task_ids = [e["id"] for e in load("tasks/registry.yaml").get("task_types", [])]
    for tf in glob.glob("triggers/**/*.yaml", recursive=True):
        if tf.endswith("registry.yaml"):
            continue
        d = load(tf)
        raw = d.get("task") or d.get("tasks") or []
        refs: list[str] = []
        if isinstance(raw, str):
            refs = [raw]
        elif isinstance(raw, dict):
            t = raw.get("type")
            if t:
                refs = [t]
        elif isinstance(raw, list):
            for item in raw:
                if isinstance(item, str):
                    refs.append(item)
                elif isinstance(item, dict) and item.get("type"):
                    refs.append(item["type"])
        for t in refs:
            if t and t not in task_ids:
                errors.append(f"{tf}: unknown task ref {t}")

    # 3. workflow steps reference real task/action ids
    act_ids = [e["id"] for e in load("actions/registry.yaml").get("actions", [])]
    for wf in glob.glob("workflows/*.yaml"):
        if wf.endswith("registry.yaml"):
            continue
        d = load(wf)
        for step in d.get("steps", []):
            if "task" in step and step["task"] not in task_ids:
                errors.append(f"{wf}: unknown task {step['task']}")
            if "action" in step and step["action"] not in act_ids:
                errors.append(f"{wf}: unknown action {step['action']}")
        trig = d.get("trigger")
        if trig and not os.path.exists(f"triggers/{trig}"):
            errors.append(f"{wf}: missing trigger file {trig}")

    # 4. agent implementation modules importable
    for af in glob.glob("agents/*.yaml"):
        if af.endswith("registry.yaml"):
            continue
        impl = load(af).get("implementation") or load(af).get("module")
        if impl:
            try:
                __import__(impl.split(".")[0])
            except ImportError:
                errors.append(f"{af}: module {impl} not importable")

    if errors:
        print("CROSS-REF ERRORS:")
        for e in errors:
            print(" -", e)
        return 1
    print("ALL REGISTRY CROSS-REFERENCES VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
