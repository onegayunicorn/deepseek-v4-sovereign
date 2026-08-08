"""Bio genomics package — variant calling pipeline.

``VariantCall`` lives in ``callers.py`` (not ``models.py``) so the
pipeline can import the callers without a circular import.
"""

from __future__ import annotations

from bio.genomics.callers import DeepVariant, KaleidoscopeCaller, VariantCall
from bio.genomics.pipeline import GenomicPipeline

__all__ = ["GenomicPipeline", "DeepVariant", "KaleidoscopeCaller", "VariantCall"]
