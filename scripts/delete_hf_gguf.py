#!/usr/bin/env python3
"""
Delete HuggingFace GGUF repository
IRREVERSIBLE — use with extreme caution. Requires explicit confirmation
(either --force with a typed override, or interactive 'DELETE <repo>').
"""

import os
import sys
import argparse
from huggingface_hub import HfApi, delete_repo

def delete_hf_repo(repo_id: str, token: str = None, force: bool = False):
    """
    Delete a HuggingFace repository.

    WARNING: This is IRREVERSIBLE. All files and history will be lost.
    """
    print(f"⚠️  WARNING: This will DELETE the repository: {repo_id}")
    print("   This action is IRREVERSIBLE.")
    print("   All files, history, and metadata will be lost.")
    print("")

    if not force:
        confirm = input(f"Type 'DELETE {repo_id}' to confirm: ")
        if confirm != f"DELETE {repo_id}":
            print("❌ Deletion cancelled.")
            return False

    try:
        api = HfApi()
        delete_repo(
            repo_id=repo_id,
            token=token or os.environ.get("HF_TOKEN"),
            repo_type="model"
        )
        print(f"✅ Repository deleted: {repo_id}")
        return True
    except Exception as e:
        print(f"❌ Deletion failed: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="Codexcoder/gemma-3-12b-it-jailbreak-EN-i1-GGUF")
    parser.add_argument("--token", help="HF token")
    parser.add_argument("--force", action="store_true", help="Skip interactive confirmation")
    args = parser.parse_args()

    delete_hf_repo(args.repo, args.token, args.force)
