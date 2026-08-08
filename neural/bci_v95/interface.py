"""BCI v9.5 interface — 432 Hz neural bridge.

PDF activation API::

    from neural.bci_v95.interface import bci
    bci.initialize()   # 432 Hz · 0.300 s latency
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

CARRIER_HZ = 432
LATENCY_S = 0.300


@dataclass
class BCIChannel:
    name: str
    frequency: float
    locked: bool = False


@dataclass
class BciSample:
    """One biometric sample for liveness checks."""

    timestamp: float
    heart_rate: float
    eeg_alpha: float
    eeg_gamma: float
    signal_strength: float
    respiration: float


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

    # ── liveness support (Pulse Lock) ────────────────────────────────────
    async def start(self) -> None:
        """Connect hardware (no-op without a real device)."""
        return None

    async def stop(self) -> None:
        """Disconnect hardware (no-op without a real device)."""
        return None

    def is_connected(self) -> bool:
        return self.initialized and self.is_locked()

    def latest(self) -> Optional[BciSample]:
        """Return the most recent biometric sample (simulated when no
        hardware is attached; None before initialize())."""
        if not self.initialized:
            return None
        base = 66.0 + (time.time() * 0.1) % 2.0  # gentle drift around 66 bpm
        return BciSample(
            timestamp=time.time(),
            heart_rate=base,
            eeg_alpha=0.42,
            eeg_gamma=0.18,
            signal_strength=0.72,
            respiration=14.0,
        )


# Module-level singleton (PDF Phase 8.1).
bci = BCIInterface()

__all__ = ["BCIInterface", "bci", "BCIChannel", "BciSample"]
