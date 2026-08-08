"""72-hour closed-loop stability test (simulated).

Simulates BCI + PERO + orchestrator under load. Marked slow; the CI
variant runs ~3 min (0.05 h). For a real soak, change the duration to 72.0.
"""

import asyncio
import statistics
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

pytestmark = pytest.mark.slow


async def _run(hours: float) -> dict:
    from neural.bci_v95.mock import MockBci
    from pero.live_ingest import LiveIngest
    from pero.tuning_agent import TuningAgent
    from quantum.entanglement_engine import EntanglementEngine

    eng = EntanglementEngine()
    eng.initialize()
    eng.generate_pairs()

    bci = MockBci(heart_rate=66.0, jitter=1.2)
    await bci.start()

    ing = LiveIngest(None, crystal="BBO")  # synthetic mode (no video/cv2 needed)
    ing.open()
    agent = TuningAgent(ing, target_fidelity=0.999423)

    deadline = time.time() + hours * 3600
    fids, efs, cohs, hrs = [], [], [], []
    try:
        async for frame in ing.stream(fps=4):
            agent.observe(frame)
            if ing.frame_num % 4 == 0:
                await agent.step()
            eng.pairs.append(("soak", frame.bell_fidelity))  # feed loop back into twins
            s = bci.latest()
            fids.append(frame.bell_fidelity)
            efs.append(frame.splitting_efficiency)
            cohs.append(frame.spatial_coherence)
            hrs.append(s.heart_rate)
            if time.time() > deadline:
                break
    finally:
        ing.close()
        await bci.stop()

    return {
        "fidelity_mean": statistics.mean(fids),
        "fidelity_min": min(fids),
        "efficiency_mean": statistics.mean(efs),
        "coherence_mean": statistics.mean(cohs),
        "hr_mean": statistics.mean(hrs),
        "samples": len(fids),
    }


@pytest.mark.asyncio
async def test_72h_closed_loop_stability():
    r = await _run(0.05)  # ~3 min in CI; change to 72.0 for a real soak
    assert r["fidelity_mean"] >= 0.992
    assert r["fidelity_min"] >= 0.975
    assert r["samples"] > 500
