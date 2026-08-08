#!/usr/bin/env python3
"""Auto-fetch any quant variant of gemma-3-12b-it-jailbreak.

Usage:
    python scripts/hf_download.py --quant Q4_K_M
    python scripts/hf_download.py --quant Q4_K_M --repo mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF
"""

import argparse
from pathlib import Path
from huggingface_hub import snapshot_download

DEFAULT_REPO = "Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF"
MIRROR_REPO = "mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF"
MODULE = Path("models/gemma-3-12b-it-jailbreak")


def download(quant: str, repo: str, force: bool) -> Path:
    dest = MODULE / "assets" / quant
    dest.mkdir(parents=True, exist_ok=True)
    if not force:
        existing = list(dest.glob("*.gguf"))
        if existing:
            print(f"already present: {existing[0]}")
            return existing[0]
    print(f"downloading {repo} ({quant}) → {dest}")
    snapshot_download(
        repo_id=repo,
        local_dir=dest,
        allow_patterns=[f"*{quant}*.gguf", "*.json", "*.imatrix"],
        force_download=force,
    )
    return dest


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quant", default="Q4_K_M")
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--mirror", action="store_true", help="use the mradermacher mirror")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    repo = MIRROR_REPO if args.mirror else args.repo
    download(args.quant, repo, args.force)
