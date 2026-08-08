"""Quimb photonic interface — tensor-network entanglement analysis.

Optional backend: ``quimb``.  Fallback computes the same tensor
quantities (bond norms, purity) with NumPy so the interface is always
importable.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

try:  # optional backend
    import quimb  # type: ignore
    QUIMB_AVAILABLE = True
except Exception:  # pragma: no cover - graceful fallback
    QUIMB_AVAILABLE = False


class QuimbInterface:
    """Quimb-backed tensor-network analysis engine."""

    backend_name = "quimb"
    available = QUIMB_AVAILABLE

    def __init__(self, seed: Optional[int] = 45) -> None:
        self.seed = seed

    def bond_norm(self, tensor: np.ndarray) -> float:
        """Frobenius norm of a lineage/tensor block."""
        return float(np.linalg.norm(np.asarray(tensor, dtype=np.float64)))

    def purity(self, bell_state: np.ndarray) -> float:
        """Purity Tr(ρ²) for a 2-qubit state."""
        psi = np.asarray(bell_state, dtype=np.complex128)
        psi = psi / np.linalg.norm(psi)
        rho = np.outer(psi, psi.conj())
        return float(np.real(np.trace(rho @ rho)))

    def analyze(self, tensor: np.ndarray) -> dict:
        t = np.asarray(tensor, dtype=np.float64)
        return {
            "shape": t.shape,
            "bond_norm": round(self.bond_norm(t), 6),
            "entries": int(t.size),
        }
