"""SOVEREIGN — pytest configuration.

Adds src/ to sys.path so tests can import ``sovereign`` directly, and
sets the minimal env the orchestrator requires at import time.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure the sovereign package (src/) and top-level PDF-spec modules
# are importable regardless of the current working directory.
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT))

# The FastAPI app constructs JWTService at import time.
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("SOVEREIGN_MODE", "test")
