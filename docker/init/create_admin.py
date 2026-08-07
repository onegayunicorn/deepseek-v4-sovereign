#!/usr/bin/env python3
"""SOVEREIGN — create an admin JWT for local API access."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from sovereign.security.authentication import JWTService  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", default="admin")
    parser.add_argument("--ttl-minutes", type=int, default=1440)
    args = parser.parse_args()
    token = JWTService().issue(args.subject, {"role": "admin"}, ttl_minutes=args.ttl_minutes)
    print(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
