"""Genomic analysis pipeline.

PDF activation API::

    pipeline = GenomicPipeline()
    pipeline.load_reference('GRCh38')
    variants = pipeline.call_variants('sample.fastq')
    deep = DeepVariant()
    deep_results = deep.call(variants)
"""

from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

import numpy as np

from bio.genomics.callers import DeepVariant, KaleidoscopeCaller, VariantCall

SUPPORTED_REFERENCES = {"GRCh37", "GRCh38", "hg19", "hg38"}


class GenomicPipeline:
    """End-to-end genomic variant calling pipeline."""

    def __init__(self, seed: Optional[int] = 23) -> None:
        self.seed = seed
        self._rng = np.random.default_rng(seed)
        self.reference: Optional[str] = None
        self.kaleidoscope_caller = KaleidoscopeCaller(seed=seed)
        self.deep_variant = DeepVariant(seed=seed + 1)

    def load_reference(self, reference: str) -> str:
        """Load a reference genome build (simulated)."""
        if reference not in SUPPORTED_REFERENCES:
            raise ValueError(f"Unsupported reference: {reference}")
        self.reference = reference
        return self.reference

    def call_variants(self, sample_path: str) -> List[VariantCall]:
        """Run variant calling over a simulated sample pileup."""
        if self.reference is None:
            raise RuntimeError("load_reference() must be called first")
        # Deterministic simulated pileup derived from the sample path.
        seed = int(hashlib.sha256(sample_path.encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        n_reads = 2000
        reads: List[Dict[str, object]] = []
        for i in range(n_reads):
            depth = int(rng.integers(20, 60))
            alt_freq = float(rng.random())
            reads.append(
                {
                    "chrom": f"chr{rng.integers(1, 23)}",
                    "pos": int(rng.integers(1, 250_000_000)),
                    "ref": "A",
                    "alt": "G",
                    "depth": depth,
                    "alt_freq": round(alt_freq, 4),
                }
            )
        variants = self.kaleidoscope_caller.call(reads)
        return variants

    def run_full(self, sample_path: str, reference: str = "GRCh38") -> Dict[str, object]:
        """Reference → call → deep-refine, returning a summary dict."""
        self.load_reference(reference)
        variants = self.call_variants(sample_path)
        refined = self.deep_variant.call(variants)
        return {
            "reference": self.reference,
            "sample": sample_path,
            "kaleidoscope_calls": len(variants),
            "deepvariant_calls": len(refined),
            "high_quality": sum(1 for v in refined if v.quality >= 40),
        }
