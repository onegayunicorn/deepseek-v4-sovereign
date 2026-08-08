"""Pulse Lock — biometric admin gate.

When enabled, /api/v1/admin/* routes require a live BCI signal with passing
liveness. No passwords. No tokens. Only your pulse.
"""

from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import dataclass
from typing import Dict, Optional

from fastapi import HTTPException, Request

from .interface import BciSample, BCIInterface

MIN_HR = 42.0
MAX_HR = 210.0
MIN_SIGNAL = 0.55
MIN_RESPIRATION = 4.0
SESSION_TTL = 15.0  # seconds — must keep BCI connected


@dataclass
class PulseSession:
    token: str
    created: float
    last_seen: float
    heart_rate: float
    signal_strength: float


class PulseLock:
    def __init__(self, bci: BCIInterface, enabled: bool = True) -> None:
        self.bci = bci
        self.enabled = enabled
        self.sessions: Dict[str, PulseSession] = {}
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        if not self.enabled:
            return
        await self.bci.start()
        self._task = asyncio.create_task(self._reaper())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
        await self.bci.stop()

    async def _reaper(self) -> None:
        try:
            while True:
                now = time.time()
                self.sessions = {
                    k: v
                    for k, v in self.sessions.items()
                    if now - v.last_seen < SESSION_TTL
                }
                await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            pass

    @staticmethod
    def _session_from_sample(s: BciSample) -> PulseSession:
        seed = f"{s.timestamp:.3f}:{s.heart_rate:.2f}:{s.eeg_alpha:.4f}:{s.eeg_gamma:.4f}"
        token = hashlib.sha256(seed.encode()).hexdigest()[:32]
        return PulseSession(
            token, time.time(), time.time(), s.heart_rate, s.signal_strength
        )

    @staticmethod
    def _liveness(s: BciSample) -> bool:
        return (
            MIN_HR <= s.heart_rate <= MAX_HR
            and s.signal_strength >= MIN_SIGNAL
            and s.respiration > MIN_RESPIRATION
        )

    async def issue(self) -> str:
        """Issue a short-lived pulse session from current BCI state."""
        if not self.enabled:
            return "pulse-disabled"
        s = self.bci.latest()
        if s is None or not self._liveness(s):
            raise HTTPException(401, "Pulse Lock: no live biometric signal")
        sess = self._session_from_sample(s)
        self.sessions[sess.token] = sess
        return sess.token

    async def refresh(self, token: str) -> bool:
        if not self.enabled:
            return True
        sess = self.sessions.get(token)
        if not sess:
            return False
        s = self.bci.latest()
        if s is None or not self._liveness(s):
            return False
        sess.last_seen = time.time()
        sess.heart_rate = s.heart_rate
        sess.signal_strength = s.signal_strength
        return True

    async def middleware(self, request: Request, call_next):
        if not self.enabled or not request.url.path.startswith("/api/v1/admin"):
            return await call_next(request)
        token = request.headers.get("X-Pulse-Token") or request.cookies.get("pulse_token")
        if not token or not await self.refresh(token):
            raise HTTPException(401, "Pulse Lock required — wear the Ring")
        return await call_next(request)
