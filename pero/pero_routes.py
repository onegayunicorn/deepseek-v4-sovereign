"""FastAPI routes for the PERO live loop.

Endpoints:
  POST /api/v1/pero/start   — start streaming + tuning
  POST /api/v1/pero/stop    — stop + release
  GET  /api/v1/pero/state   — latest frame + tuning state
  WS   /api/v1/pero/stream  — push frames to browsers

Note: `cv2` is optional — with no source the ingest runs in synthetic mode.
"""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .live_ingest import get_or_create_ingest
from .tuning_agent import TuningAgent

router = APIRouter(prefix="/api/v1/pero", tags=["pero"])

_ws_clients: set[WebSocket] = set()
_state: dict = {"agent": None, "task": None}


class TuneRequest(BaseModel):
    source: str = "data/raw/videos/20260807_223101.mp4"
    crystal: str = "BBO"
    target_fidelity: float = 0.999423
    fps: int = 10


@router.post("/start")
async def pero_start(req: TuneRequest):
    ing = get_or_create_ingest(req.source, crystal=req.crystal)
    ing.open()
    agent = TuningAgent(ing, target_fidelity=req.target_fidelity)
    _state["agent"] = agent
    _state["task"] = asyncio.create_task(_run_loop(ing, agent, req.fps))
    return {"status": "running", "crystal": req.crystal, "target": req.target_fidelity}


@router.post("/stop")
async def pero_stop():
    t = _state.get("task")
    if t:
        t.cancel()
    ing = next(iter(get_or_create_ingest.__globals__.get("_ingest_cache", {}).values()), None)
    if ing:
        ing.close()
    return {"status": "stopped"}


@router.get("/state")
async def pero_state():
    agent = _state.get("agent")
    if not agent or not agent.history:
        return {"running": False}
    f = agent.history[-1]
    return {
        "running": True,
        "frame": f.__dict__,
        "pairs_total": agent.ingest.pairs_total,
        "last_tune": agent.last_rec.__dict__ if agent.last_rec else None,
    }


async def _run_loop(ing, agent, fps: int) -> None:
    try:
        async for frame in ing.stream(fps):
            agent.observe(frame)
            if agent.ingest.frame_num % fps == 0:
                await agent.step()
            msg = json.dumps(
                {"type": "pero", "frame": frame.__dict__, "pairs": agent.ingest.pairs_total}
            )
            for ws in list(_ws_clients):
                try:
                    await ws.send_text(msg)
                except Exception:
                    _ws_clients.discard(ws)
    except asyncio.CancelledError:
        pass


@router.websocket("/stream")
async def pero_ws(ws: WebSocket):
    await ws.accept()
    _ws_clients.add(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        _ws_clients.discard(ws)
