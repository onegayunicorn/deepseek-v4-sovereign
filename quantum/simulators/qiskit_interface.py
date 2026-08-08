"""Qiskit photonic interface — Bell pair generation.

Uses Qiskit when installed; otherwise a NumPy fallback implementing the
same API (``generate_bell_pairs`` / ``measure_fidelity``).
"""

from __future__ import annotations

import math
from typing import List, Optional

import numpy as np

try:  # optional backend
    from qiskit import QuantumCircuit, Aer, execute  # type: ignore
    QISKIT_AVAILABLE = True
except Exception:  # pragma: no cover - graceful fallback
    QISKIT_AVAILABLE = False

_BELL = np.array([1.0, 0.0, 0.0, 1.0]) / math.sqrt(2.0)


class QiskitInterface:
    """Qiskit-backed Bell state pair generator."""

    backend_name = "qiskit"
    available = QISKIT_AVAILABLE

    def __init__(self, seed: Optional[int] = 42) -> None:
        self.seed = seed
        self._rng = np.random.default_rng(seed)
        self.circuits: List[object] = []

    def generate_bell_pairs(self, count: int) -> np.ndarray:
        """Return an array of shape (count, 4) of Bell states."""
        if count <= 0:
            raise ValueError("count must be positive")
        if QISKIT_AVAILABLE:
            return self._generate_qiskit(count)
        return self._generate_numpy(count)

    def measure_fidelity(self, states: np.ndarray) -> float:
        """Mean fidelity of ``states`` against the ideal |Φ⁺⟩."""
        arr = np.asarray(states, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr[None, :]
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        arr = np.divide(arr, norms, out=np.zeros_like(arr), where=norms > 0)
        fids = np.einsum("ij,j->i", arr, _BELL) ** 2
        return float(np.mean(fids))

    # ── internals ─────────────────────────────────────────────────────
    def _generate_qiskit(self, count: int) -> np.ndarray:
        """Build H+CNOT circuits and read the ideal statevector."""
        from qiskit import QuantumCircuit, Aer
        from qiskit.providers.aer import QasmSimulator

        simulator = Aer.get_backend("qasm_simulator")
        states = []
        for _ in range(count):
            qc = QuantumCircuit(2, 2)
            qc.h(0)
            qc.cx(0, 1)
            qc.measure_all()
            self.circuits.append(qc)
            # statevector path for exactness
            from qiskit import Aer as _Aer

            sv_sim = _Aer.get_backend("statevector_simulator")
            result = execute(qc.remove_final_measurements(inplace=False), sv_sim).result()
            sv = np.asarray(result.get_statevector(qc.remove_final_measurements(inplace=False)))
            states.append(np.real(sv))
        return np.stack(states)

    def _generate_numpy(self, count: int) -> np.ndarray:
        noise = self._rng.normal(0.0, 1e-4, size=(count, 4))
        states = np.tile(_BELL, (count, 1)) + noise
        states /= np.linalg.norm(states, axis=1, keepdims=True)
        return states
