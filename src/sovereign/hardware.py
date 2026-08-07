"""SOVEREIGN — hardware manager (Sovereign Ring BCI + Sovereign Buds).

Bridges the monorepo's hardware adapters (``hardware/bci-ring`` and
``hardware/earbuds``) into the orchestrator runtime. Adapters are imported
defensively — the orchestrator runs fine with no hardware attached.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from sovereign.utils.logging import get_logger

logger = get_logger("hardware")

_MONOREPO = Path(__file__).resolve().parent.parent.parent.parent  # deepseek-v4-sovereign/


def _load_adapter(module_path: str) -> Any:
    spec = importlib.util.spec_from_file_location("sovereign_hardware_adapter", module_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["sovereign_hardware_adapter"] = module
    spec.loader.exec_module(module)
    return module


class HardwareManager:
    """Registry of connected sovereign devices."""

    def __init__(self) -> None:
        self.devices: dict[str, Any] = {}
        self._discover()

    def _discover(self) -> None:
        candidates = {
            "bci-ring": _MONOREPO / "hardware" / "bci-ring" / "driver_adapter.py",
            "earbuds": _MONOREPO / "hardware" / "earbuds" / "driver_adapter.py",
        }
        for name, path in candidates.items():
            if not path.exists():
                logger.debug("hardware adapter not found: %s", path)
                continue
            try:
                module = _load_adapter(str(path))
                cls = getattr(module, {"bci-ring": "BciRingAdapter", "earbuds": "SovereignBudsAdapter"}[name], None)
                if cls is not None:
                    self.devices[name] = cls()
            except Exception:  # noqa: BLE001
                logger.warning("failed to load hardware adapter %s", name)

    async def status(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for name, device in self.devices.items():
            try:
                result[name] = device.status()
            except Exception as exc:  # noqa: BLE001
                result[name] = {"error": str(exc)}
        return result

    async def list(self) -> list[str]:
        return list(self.devices)

    def device(self, name: str) -> Any | None:
        return self.devices.get(name)
