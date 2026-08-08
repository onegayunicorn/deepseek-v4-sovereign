"""PERO live-loop tests — synthetic mode (no opencv/video required)."""

import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_live_ingest_synthetic_metrics():
    from pero.live_ingest import LiveIngest

    with LiveIngest(None, crystal="BBO", wavelength_nm=532) as ing:
        frames = [ing._metrics_from_frame(ing._synthetic_frame()) for _ in range(3)]
    assert len(frames) == 3
    for f in frames:
        assert 0.95 <= f.bell_fidelity <= 0.9999
        assert 0.3 <= f.splitting_efficiency <= 0.75
        assert 0.4 <= f.spatial_coherence <= 0.92
        assert f.pairs_this_frame >= 1
    # fidelity trend must land near target at optimum temp
    assert frames[-1].bell_fidelity > 0.98


def test_tuning_agent_recommends():
    from pero.live_ingest import LiveIngest
    from pero.tuning_agent import TuningAgent

    ing = LiveIngest(None, crystal="BBO")
    agent = TuningAgent(ing, target_fidelity=0.999423)
    for i in range(30):
        f = ing._metrics_from_frame(ing._synthetic_frame())
        agent.observe(f)
    rec = agent.recommend()
    assert rec.confidence > 0.0
    assert rec.rationale  # non-empty


@pytest.mark.asyncio
async def test_stream_yields_frames():
    from pero.live_ingest import LiveIngest
    from pero.tuning_agent import TuningAgent

    ing = LiveIngest(None, crystal="KTP")
    agent = TuningAgent(ing, target_fidelity=0.999423)
    n = 0
    async for frame in ing.stream(fps=100):
        agent.observe(frame)
        n += 1
        if n >= 5:
            break
    assert n == 5
    assert ing.pairs_total > 0
    rec = agent.recommend()
    assert rec.confidence > 0.25


@pytest.mark.asyncio
async def test_tuning_step_moves_temperature():
    from pero.live_ingest import LiveIngest
    from pero.tuning_agent import TuningAgent

    ing = LiveIngest(None, crystal="BBO")
    agent = TuningAgent(ing)
    for _ in range(30):
        agent.observe(ing._metrics_from_frame(ing._synthetic_frame()))
    before = ing.temperature_c
    rec = await agent.step()
    assert rec is not None
    # temperature stays near the crystal optimum (-21 C for BBO); power
    # rises when fidelity trails the target (proportional control)
    assert abs(ing.temperature_c - (-21.0)) <= 0.5
    assert abs(ing.temperature_c - before) <= 0.5
    assert ing.power_mw >= 150.0


def test_ws_bridge_payload_shape():
    import json

    from pero.live_ingest import LiveIngest
    from pero.pero_ws_bridge import attach_pero_to_orchestrator_ws

    captured = {}

    async def broadcast(payload):
        captured.update(payload)

    ing = LiveIngest(None, crystal="BBO")
    listener = attach_pero_to_orchestrator_ws(broadcast)
    f = ing._metrics_from_frame(ing._synthetic_frame())
    asyncio.run(listener(f))
    assert captured["type"] == "pero"
    assert "bell_fidelity" in captured["data"]
