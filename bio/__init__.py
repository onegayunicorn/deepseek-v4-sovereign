"""SOVEREIGN — bio module (DNA resonance + genomic pipeline).

Top-level ``bio`` package per the PDF activation spec::

    from bio.dna.harmonic_resonance import HarmonicResonanceEngine
    from bio.dna.kaleidoscope import KaleidoscopeEngine
    from bio.genomics.pipeline import GenomicPipeline
    from bio.genomics.callers import DeepVariant, KaleidoscopeCaller
"""

from __future__ import annotations

from bio.dna.awakening import DNAAwakeningEngine
from bio.dna.harmonic_resonance import HarmonicResonanceEngine
from bio.dna.kaleidoscope import KaleidoscopeEngine
from bio.genomics.callers import DeepVariant, KaleidoscopeCaller, VariantCall
from bio.genomics.pipeline import GenomicPipeline

__all__ = [
    "DNAAwakeningEngine",
    "HarmonicResonanceEngine",
    "KaleidoscopeEngine",
    "GenomicPipeline",
    "DeepVariant",
    "KaleidoscopeCaller",
    "VariantCall",
]
