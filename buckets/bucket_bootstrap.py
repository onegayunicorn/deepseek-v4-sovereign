#!/usr/bin/env python3
"""SOVEREIGN — bucket bootstrap.

Reads buckets/sovereign-bucket.yaml and provisions the bucket layout.
Runs in dry-run mode by default (no cloud API calls) and prints the exact
plan. With --apply it calls the OGU multi-cloud manager (../buckets) when
importable, otherwise prints the provider CLI commands to run manually.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # monorepo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))  # package root

from sovereign.utils.serialization import load_yaml  # noqa: E402

BUCKET_CFG = Path(__file__).resolve().parent / "sovereign-bucket.yaml"
MONOREPO = Path(__file__).resolve().parent.parent


def load_plan() -> dict:
    return load_yaml(BUCKET_CFG)


def render_plan(plan: dict) -> str:
    lines = [f"# Sovereign bucket plan (provider={plan['providers']['primary']})"]
    for bucket in plan["buckets"]:
        lines.append(f"\n[{bucket['id']}] {bucket['name']}")
        lines.append(f"  purpose : {bucket['purpose']}")
        lines.append(f"  access  : {bucket['access']}  versioning: {bucket['versioning']}")
        for rule in bucket.get("lifecycle", []):
            lines.append(f"  lifecycle: {rule['action']} day={rule['days']} to={rule.get('to', '-')}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Provision sovereign buckets")
    parser.add_argument("--apply", action="store_true", help="Actually provision (default: dry-run)")
    parser.add_argument("--env", default="dev", help="Environment suffix for bucket names")
    args = parser.parse_args()

    plan = load_plan()
    if not args.apply:
        print(render_plan(plan))
        print("\n[DRY-RUN] no cloud resources were created.")
        print("Run with --apply to provision via the OGU bucket manager.")
        return 0

    # Attempt integration with the existing multi-cloud manager.
    manager_path = MONOREPO.parent / "buckets" / "bucket_manager.py"
    if manager_path.exists():
        sys.path.insert(0, str(manager_path.parent))
        try:
            from bucket_manager import BucketManager  # type: ignore

            manager = BucketManager()
            for bucket in plan["buckets"]:
                name = bucket["name"].replace("${ENV}", args.env)
                print(f"provisioning {name} ...")
                manager.ensure_bucket(name, region="us-east-1", versioning=bucket["versioning"])
            print("ALL BUCKETS PROVISIONED")
            return 0
        except ImportError as exc:
            print(f"[warn] bucket_manager import failed: {exc} — falling back to CLI notes")
        except Exception as exc:  # noqa: BLE001
            print(f"[error] provisioning failed: {exc}")
            return 1

    print(render_plan(plan))
    print("\nApply manually with (example, AWS):")
    for bucket in plan["buckets"]:
        name = bucket["name"].replace("${ENV}", args.env)
        print(f'  aws s3api create-bucket --bucket {name} --region us-east-1')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
