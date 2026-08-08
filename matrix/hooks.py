"""Matrix lifecycle hooks (follow the repo hook pattern)."""

from __future__ import annotations

from typing import Any, Dict

from .evolution import EpochReport
from .integration import RealityMatrix


def on_matrix_integrate(matrix: RealityMatrix, engine: Any = None) -> Dict[str, object]:
    """Hook fired after the matrix binds engine state."""
    if engine is not None:
        matrix.from_engine(engine)
    state = matrix.to_dict()
    print(f"matrix integrated: {state}")
    return state


def on_matrix_evolve(report: EpochReport) -> Dict[str, object]:
    """Hook fired after an evolution epoch."""
    payload = {
        "epoch": report.epoch,
        "branches_before": report.branches_before,
        "branches_after": report.branches_after,
        "entropy": report.entropy,
        "coherence": report.coherence,
        "pruned": report.pruned,
    }
    print(f"matrix evolved: epoch={report.epoch} branches={report.branches_after}")
    return payload
