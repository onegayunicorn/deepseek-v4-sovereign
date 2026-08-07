"""SOVEREIGN — pytest configuration.

Adds src/ to sys.path so tests can import ``sovereign`` directly.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
