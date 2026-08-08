"""FastAPI routes for the Pulse Lock."""

from __future__ import annotations

from fastapi import APIRouter, Response

from .pulse_lock import PulseLock


def make_pulse_routes(lock: PulseLock) -> APIRouter:
    r = APIRouter(prefix="/api/v1/pulse", tags=["pulse"])

    @r.post("/issue")
    async def pulse_issue(resp: Response):
        tok = await lock.issue()
        resp.set_cookie(
            "pulse_token", tok, httponly=True, samesite="strict", max_age=15
        )
        return {"token": tok, "ttl_seconds": 15}

    @r.get("/status")
    async def pulse_status():
        s = lock.bci.latest()
        return {
            "enabled": lock.enabled,
            "connected": lock.bci.is_connected(),
            "heart_rate": s.heart_rate if s else None,
            "signal_strength": s.signal_strength if s else None,
            "active_sessions": len(lock.sessions),
        }

    return r
