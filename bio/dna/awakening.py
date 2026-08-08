"""DNA awakening engine — orchestrates resonance + kaleidoscope.

Exposes a single ``awaken()`` entry point used by the sovereign
autonomous loop: runs the resonance waves, sweeps the kaleidoscope
permutations and reports the composite awakening metric.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from bio.dna.harmonic_resonance import HarmonicResonanceEngine
from bio.dna.kaleidoscope import KaleidoscopeEngine


@dataclass
class AwakeningResult:
    awakening_pct: float
    threshold_pct: float
    exceeded: bool
    kaleidoscope_perms: int
    strands: int


class DNAAwakeningEngine:
    """Composite DNA awakening orchestrator."""

    def __init__(self, strands: int = 10000, waves: int = 100) -> None:
        self.strands = strands
        self.waves = waves
        self.resonance = HarmonicResonanceEngine()
        self.kaleidoscope = KaleidoscopeEngine()

    def awaken(self) -> AwakeningResult:
        self.resonance.initialize_strands(self.strands)
        for _ in range(self.waves):
            self.resonance.apply_recursive_wave(100)
        kaleido = self.kaleidoscope.sweep_all_permutations()
        pct = self.resonance.current_awakening * 100
        return AwakeningResult(
            awakening_pct=round(pct, 1),
            threshold_pct=self.resonance.threshold * 100,
            exceeded=self.resonance.current_awakening > self.resonance.threshold,
            kaleidoscope_perms=kaleido["completed"],
            strands=self.strands,
        )
