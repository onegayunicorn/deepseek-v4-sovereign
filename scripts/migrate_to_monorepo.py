#!/usr/bin/env python3
"""Migration helper: re-point module config from the HF source repo to the
mirror (used if the source GGUF repo is deleted to free quota)."""

import argparse
import re
import sys
from pathlib import Path

MODULE = Path("models/gemma-3-12b-it-jailbreak")
SOURCE = "Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF"
MIRROR = "mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF"


def migrate(dry_run: bool = True) -> int:
    changed = []
    for p in MODULE.rglob("*"):
        if p.suffix not in (".yaml", ".py", ".md", ".sh"):
            continue
        text = p.read_text(encoding="utf-8")
        if SOURCE in text:
            new = text.replace(SOURCE, MIRROR)
            changed.append(str(p))
            if not dry_run:
                p.write_text(new, encoding="utf-8")
    for c in changed:
        print(("would update" if dry_run else "updated"), c)
    if not changed:
        print("no references to update")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually rewrite files")
    args = ap.parse_args()
    sys.exit(migrate(dry_run=not args.apply))
