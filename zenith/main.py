"""Zenith CLI — ``python -m zenith.main verify`` (PDF Phase 9.1)."""

from __future__ import annotations

import sys

from zenith.os import zenith


def verify() -> None:
    """Print the final verification dashboard."""
    result = zenith.verify()
    print("[STATED-AS-IS] Tick 21,600")
    print(f"{'Component':<20} {'Status':<12} Metric")
    print("-" * 46)
    for comp in result["components"]:
        print(f"{comp['name']:<20} {comp['status']:<12} {comp['metric']}")
    if result["all_nominal"]:
        print("All systems nominal. Manifestation confirmed.")
    return None


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if command == "verify":
        verify()
    else:
        print(f"unknown command: {command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
