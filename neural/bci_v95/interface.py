"""BCI v9.5 interface — 432 Hz neural bridge.

PDF activation API::

    from neural.bci_v95.interface import bci
    bci.initialize()   # 432 Hz · 0.300 s latency
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

CARRIER_HZ = 432
LATENCY_S = 0.300


@dataclass
class BCIChannel:
    name: str
    frequency: float
    locked: bool = False


class BCIInterface:
    """Neural interface locked to the 432 Hz carrier."""

    def __init__(self) -> None:
        self.initialized = False
        self.channels: List[BCIChannel] = []
        self.carrier_hz = CARRIER_HZ
        self.latency_s = LATENCY_S

    def initialize(self) -> "BCIInterface":
        self.channels = [
            BCIChannel(name="alpha", frequency=8.0),
            BCIChannel(name="beta", frequency=18.0),
            BCIChannel(name="gamma", frequency=40.0),
            BCIChannel(name="carrier", frequency=float(CARRIER_HZ)),
        ]
        for channel in self.channels:
            channel.locked = True
        self.initialized = True
        return self

    def is_locked(self) -> bool:
        return self.initialized and all(c.locked for c in self.channels)

    def summary(self) -> Dict[str, object]:
        return {
            "initialized": self.initialized,
            "carrier_hz": self.carrier_hz,
            "latency_s": self.latency_s,
            "locked": self.is_locked(),
            "channels": len(self.channels),
        }


# Module-level singleton (PDF Phase 8.1).
bci = BCIInterface()

__all__ = ["BCIInterface", "bci", "BCIChannel"]
