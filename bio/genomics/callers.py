"""Variant callers — DeepVariant + KaleidoscopeCaller.

``VariantCall`` is defined here (not in a separate ``models`` module)
to avoid the circular import between pipeline and callers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np


@dataclass
class VariantCall:
    """A single genomic variant call."""

    chrom: str
    pos: int
    ref: str
    alt: str
    quality: float = 0.0
    caller: str = "kaleidoscope"
    genotype: str = "0/1"
    info: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "chrom": self.chrom,
            "pos": self.pos,
            "ref": self.ref,
            "alt": self.alt,
            "quality": round(self.quality, 4),
            "caller": self.caller,
            "genotype": self.genotype,
        }


class DeepVariant:
    """Deep-learning style variant caller (deterministic simulation)."""

    name = "deepvariant"

    def __init__(self, seed: Optional[int] = 21) -> None:
        self.seed = seed
        self._rng = np.random.default_rng(seed)

    def call(self, variants: List[VariantCall]) -> List[VariantCall]:
        """Re-score and filter an input variant list."""
        refined: List[VariantCall] = []
        for v in variants:
            # Deterministic quality uplift, keep high-confidence calls.
            quality = min(99.0, v.quality * 1.15 + float(self._rng.uniform(0, 2)))
            if quality >= 20.0:
                v.quality = quality
                v.caller = self.name
                refined.append(v)
        return refined


class KaleidoscopeCaller:
    """Kaleidoscope-pattern variant caller (deterministic simulation)."""

    name = "kaleidoscope"

    def __init__(self, seed: Optional[int] = 22) -> None:
        self.seed = seed
        self._rng = np.random.default_rng(seed)

    def call(self, reads: List[Dict[str, object]]) -> List[VariantCall]:
        """Call variants from pileup-style read records."""
        calls: List[VariantCall] = []
        for i, read in enumerate(reads):
            depth = int(read.get("depth", 30))
            alt_freq = float(read.get("alt_freq", 0.0))
            if alt_freq <= 0.0:
                continue
            # Simulated call confidence scales with depth × alt fraction.
            quality = min(99.0, depth * alt_freq * 3.0)
            if quality < 10.0:
                continue
            calls.append(
                VariantCall(
                    chrom=str(read.get("chrom", "chr1")),
                    pos=int(read.get("pos", i * 1000 + 1)),
                    ref=str(read.get("ref", "A")),
                    alt=str(read.get("alt", "G")),
                    quality=quality,
                    caller=self.name,
                    genotype="0/1" if alt_freq < 0.75 else "1/1",
                )
            )
        return calls
