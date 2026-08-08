"""Test suite — gemma-3-12b-it-jailbreak integration.

Run from the repo root: python -m pytest models/gemma-3-12b-it-jailbreak/tests
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
MOD = ROOT / "models" / "gemma-3-12b-it-jailbreak"

# repo root (for scripts-style imports) + module root (for hooks/tasks)
for p in (ROOT, MOD):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
