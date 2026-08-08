#!/usr/bin/env python3
"""Sync HF repo metadata into the monorepo module card.

Pulls model card fields (downloads, updated, tags) and writes a JSON
snapshot under models/gemma-3-12b-it-jailbreak/docs/. Read-only on HF.
"""

import argparse
import json
import os
import sys
from pathlib import Path

REPO = "Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF"
OUT = Path("models/gemma-3-12b-it-jailbreak/docs/hf_snapshot.json")


def sync(repo: str) -> int:
    from huggingface_hub import HfApi

    api = HfApi()
    try:
        info = api.model_info(repo, token=os.environ.get("HF_TOKEN"))
    except Exception as e:
        print(f"sync failed: {e}", file=sys.stderr)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "repo_id": info.id,
        "downloads": getattr(info, "downloads", None),
        "last_modified": str(getattr(info, "last_modified", "")),
        "private": getattr(info, "private", None),
        "tags": list(getattr(info, "tags", []) or []),
        "library_name": getattr(info, "library_name", None),
    }
    OUT.write_text(json.dumps(snapshot, indent=2))
    print(f"synced → {OUT}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    args = ap.parse_args()
    sys.exit(sync(args.repo))
