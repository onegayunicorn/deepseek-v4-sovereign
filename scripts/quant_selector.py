#!/usr/bin/env python3
"""Hardware-optimized quant picker (CLI wrapper around the module task)."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tasks.quant_selector import select_quant  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ram", type=float, default=8.0)
    ap.add_argument("--use-case", default="balanced", choices=["speed", "quality", "balanced"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    res = select_quant(
        {"ram_gb": args.ram, "is_cpu": True, "use_case": args.use_case}
    )
    if args.json:
        print(json.dumps(res, indent=2))
        return 0
    if "error" in res:
        print(f"ERROR: {res['error']}", file=sys.stderr)
        return 1
    print(
        f"selected: {res['selected']['id']} ({res['selected']['size_gb']:.2f} GB) "
        f"| {res['ram_used']:.2f}/{res['ram_available']:.2f} GB used"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
