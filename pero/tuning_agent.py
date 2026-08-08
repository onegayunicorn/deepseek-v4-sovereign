"""PERO tuning agent — closes the photonic feedback loop.

Receives frame metrics → recommends optimal laser params (proportional
control toward the crystal's temperature optimum and target fidelity).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .live_ingest import CRYSTAL_RESPONSE, LaserFrame, LiveIngest


@dataclass
class TuneRecommendation:
    power_mw_delta: float
    temperature_c_delta: float
    wavelength_nm_delta: int
    crystal_swap: Optional[str]
    confidence: float
    rationale: str


class TuningAgent:
    def __init__(self, ingest: LiveIngest, target_fidelity: float = 0.999423) -> None:
        self.ingest = ingest
        self.target_fidelity = target_fidelity
        self.history: list[LaserFrame] = []
        self.last_rec: Optional[TuneRecommendation] = None

    def observe(self, f: LaserFrame) -> None:
        self.history.append(f)
        if len(self.history) > 300:
            self.history.pop(0)

    def recommend(self) -> TuneRecommendation:
        if not self.history:
            return TuneRecommendation(0.0, 0.0, 0, None, 0.0, "no data")
        recent = self.history[-30:]
        fid = sum(f.bell_fidelity for f in recent) / len(recent)
        eff = sum(f.splitting_efficiency for f in recent) / len(recent)
        coh = sum(f.spatial_coherence for f in recent) / len(recent)
        resp = CRYSTAL_RESPONSE[self.ingest.crystal]
        # Proportional control toward optimum
        t_err = resp["temp_opt"] - self.ingest.temperature_c
        fid_err = self.target_fidelity - fid
        pwr_delta = 6.0 * fid_err / max(0.001, 1 - fid_err)
        t_delta = 0.6 * t_err - 4.0 * fid_err
        conf = float(min(1.0, 0.4 + 0.6 * (1 - abs(fid_err))))
        rationale = (
            f"F={fid:.6f} (err={fid_err:+.6f}) η={eff:.3f} γ={coh:.3f} "
            f"T={self.ingest.temperature_c:+.1f}°C opt={resp['temp_opt']:+.1f}°C"
        )
        return TuneRecommendation(pwr_delta, t_delta, 0, None, conf, rationale)

    async def step(self) -> Optional[TuneRecommendation]:
        rec = self.recommend()
        if rec.confidence < 0.25:
            return None
        self.ingest.tune(
            power_mw=self.ingest.power_mw + rec.power_mw_delta,
            temperature_c=self.ingest.temperature_c + rec.temperature_c_delta,
            wavelength_nm=self.ingest.wavelength_nm + rec.wavelength_nm_delta,
        )
        self.last_rec = rec
        return rec
