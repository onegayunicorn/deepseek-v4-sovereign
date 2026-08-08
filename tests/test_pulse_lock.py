"""Pulse Lock tests — liveness gate + session lifecycle (MockBci)."""

import asyncio
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _fresh_lock(bci):
    from neural.bci_v95.pulse_lock import PulseLock

    return PulseLock(bci, enabled=True)


@pytest.mark.asyncio
async def test_issue_with_live_signal():
    from neural.bci_v95.mock import MockBci
    from neural.bci_v95.pulse_lock import PulseLock

    bci = MockBci(heart_rate=66.0, jitter=1.2)
    lock = PulseLock(bci, enabled=True)
    tok = await lock.issue()
    assert tok != "pulse-disabled"
    assert len(tok) == 32
    assert tok in lock.sessions


@pytest.mark.asyncio
async def test_issue_denied_without_signal():
    from neural.bci_v95.interface import BCIInterface
    from neural.bci_v95.pulse_lock import PulseLock

    from fastapi import HTTPException

    bci = BCIInterface()  # not initialized → latest() is None
    lock = PulseLock(bci, enabled=True)
    with pytest.raises(HTTPException) as exc:
        await lock.issue()
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_extends_session():
    from neural.bci_v95.mock import MockBci
    from neural.bci_v95.pulse_lock import PulseLock

    bci = MockBci()
    lock = PulseLock(bci, enabled=True)
    tok = await lock.issue()
    assert await lock.refresh(tok) is True


@pytest.mark.asyncio
async def test_refresh_fails_for_unknown_token():
    from neural.bci_v95.mock import MockBci
    from neural.bci_v95.pulse_lock import PulseLock

    lock = PulseLock(MockBci(), enabled=True)
    assert await lock.refresh("bogus") is False


def test_liveness_thresholds():
    from neural.bci_v95.interface import BciSample
    from neural.bci_v95.pulse_lock import PulseLock

    def sample(hr, sig, resp):
        return BciSample(time.time(), hr, 0.4, 0.2, sig, resp)

    assert PulseLock._liveness(sample(66, 0.72, 14.0)) is True
    assert PulseLock._liveness(sample(30, 0.72, 14.0)) is False  # HR too low
    assert PulseLock._liveness(sample(66, 0.30, 14.0)) is False  # weak signal
    assert PulseLock._liveness(sample(66, 0.72, 2.0)) is False   # apnea


@pytest.mark.asyncio
async def test_disabled_lock_always_passes():
    from neural.bci_v95.interface import BCIInterface
    from neural.bci_v95.pulse_lock import PulseLock

    lock = PulseLock(BCIInterface(), enabled=False)
    assert await lock.issue() == "pulse-disabled"
    assert await lock.refresh("anything") is True
