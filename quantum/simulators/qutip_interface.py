"""QuTiP photonic interface — density-matrix entanglement metrics.

Optional backend: ``qutip``.  Fallback computes concurrence / von
Neumann entropy with NumPy + SciPy directly.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

try:  # optional backend
    import qutip  # type: ignore
    QUTIP_AVAILABLE = True
except Exception:  # pragma: no cover - graceful fallback
    QUTIP_AVAILABLE = False

_BELL = np.array([1.0, 0.0, 0.0, 1.0]) / np.sqrt(2.0)


class QutipInterface:
    """QuTiP-backed entanglement metric engine."""

    backend_name = "qutip"
    available = QUTIP_AVAILABLE

    def __init__(self, seed: Optional[int] = 44) -> None:
        self.seed = seed

    def density_matrix(self, bell_state: np.ndarray) -> np.ndarray:
        """Build the 4×4 density matrix from a pure state."""
        psi = np.asarray(bell_state, dtype=np.complex128)
        psi = psi / np.linalg.norm(psi)
        return np.outer(psi, psi.conj())

    def concurrence(self, bell_state: np.ndarray) -> float:
        """Wootters concurrence for a 2-qubit state."""
        rho = self.density_matrix(bell_state)
        y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
        rho_tilde = np.kron(y, y) @ np.conj(rho) @ np.kron(y, y)
        ev = np.linalg.eigvalsh(rho @ rho_tilde)
        lam = np.sort(np.sqrt(np.maximum(np.real(ev), 0.0)))[::-1]
        return float(max(0.0, lam[0] - lam[1] - lam[2] - lam[3]))

    def entropy(self, bell_state: np.ndarray) -> float:
        """von Neumann entropy S = -Tr(ρ log₂ ρ)."""
        rho = self.density_matrix(bell_state)
        ev = np.linalg.eigvalsh(rho)
        ev = ev[ev > 1e-15]
        return float(-np.sum(ev * np.log2(ev)))
