"""
Download Model Task — Fetch any quant variant from HuggingFace
"""

import os
import argparse
from pathlib import Path
from huggingface_hub import snapshot_download

def download_model(
    quant: str = "Q4_K_M",
    model_id: str = "mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF",
    local_dir: str = None,
    force: bool = False
):
    """
    Download model from HuggingFace to local directory.
    """
    if local_dir is None:
        local_dir = f"models/gemma-3-12b-it-jailbreak/assets/{quant}/"

    local_path = Path(local_dir)
    local_path.mkdir(parents=True, exist_ok=True)

    # Check if already downloaded
    if not force:
        existing = list(local_path.glob("*.gguf"))
        if existing:
            print(f"✅ Model already exists: {existing[0]}")
            return str(existing[0])

    print(f"📥 Downloading {model_id} ({quant})...")

    try:
        # Download specific quant
        downloaded = snapshot_download(
            repo_id=model_id,
            local_dir=local_path,
            allow_patterns=[f"*{quant}*.gguf", "*.json"],
            force_download=force
        )
        print(f"✅ Model downloaded to: {local_path}")
        return str(local_path)
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quant", default="Q4_K_M")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    download_model(args.quant, force=args.force)
