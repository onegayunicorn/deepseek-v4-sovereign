"""Mock BCI for tests and the closed-loop soak harness."""

from __future__ import annotations

import time
from typing import Optional

from .interface import BciSample, BCIInterface


class MockBci(BCIInterface):
    """Deterministic mock with configurable jitter (no hardware)."""

    def __init__(self, heart_rate: float = 66.0, jitter: float = 1.2) -> None:
        super().__init__()
        self._heart_rate = heart_rate
        self._jitter = jitter
        self.initialize()

    def latest(self) -> Optional[BciSample]:
        drift = (time.time() * 1.7) % self._jitter
        return BciSample(
            timestamp=time.time(),
            heart_rate=self._heart_rate + drift,
            eeg_alpha=0.42,
            eeg_gamma=0.18,
            signal_strength=0.72,
            respiration=14.0,
        )
