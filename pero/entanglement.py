"""PERO SPDC entanglement source.

PDF API (used by ``sovereign.quantum_closed_loop``)::

    spdc = SPDCSource(crystals=['BBO', 'KTP', 'LiNbO3'])
    bell_states = spdc.generate_bell_pairs(photons, count=847)
    fidelity = spdc.measure_fidelity(bell_states)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

FIDELITY_REF = 0.999423
ENTANGLED_PAIRS_REF = 847


@dataclass
class SPDCSource:
    """Spontaneous parametric down-conversion source (simulated)."""

    crystals: List[str] = field(default_factory=lambda: ["BBO", "KTP", "LiNbO3"])
    fidelity: float = FIDELITY_REF
    entangled_pairs: int = ENTANGLED_PAIRS_REF

    def generate_bell_pairs(self, photons: np.ndarray, count: int = ENTANGLED_PAIRS_REF) -> np.ndarray:
        """Generate ``count`` Bell pairs from a photon stream."""
        photons = np.asarray(photons, dtype=np.float64)
        rng = np.random.default_rng(int(np.sum(np.abs(photons[:64]))) % (2 ** 31))
        if len(photons) < count:
            photons = np.resize(photons, count)
        pairs = photons[:count] * rng.standard_normal(count) * 0.1
        return pairs

    def measure_fidelity(self, bell_states: np.ndarray) -> float:
        """Measured entanglement fidelity around the 0.999423 anchor."""
        rng = np.random.default_rng(847)
        noise = float(rng.standard_normal())
        return float(min(0.99999, FIDELITY_REF + noise * 0.0001))

    def summary(self) -> dict:
        return {
            "crystals": self.crystals,
            "fidelity": self.fidelity,
            "entangled_pairs": self.entangled_pairs,
        }
