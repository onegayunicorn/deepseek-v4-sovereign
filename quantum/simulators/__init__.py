"""Photonic simulator interfaces — Qiskit / Cirq / QuTiP / Quimb.

Each interface exposes the PDF activation API::

    qiskit = QiskitInterface()
    bell_pairs = qiskit.generate_bell_pairs(847)
    photonic_state = cirq.create_photonic_entanglement(bell_pairs)

All four import cleanly even when the optional backend package is not
installed — the fallback path implements the same API with NumPy so the
orchestrator never hard-fails on a missing dependency.
"""

from __future__ import annotations

from quantum.simulators.qiskit_interface import QiskitInterface
from quantum.simulators.cirq_interface import CirqInterface
from quantum.simulators.qutip_interface import QutipInterface
from quantum.simulators.quimb_interface import QuimbInterface

AVAILABLE_SIMULATORS = [QiskitInterface, CirqInterface, QutipInterface, QuimbInterface]

__all__ = [
    "QiskitInterface",
    "CirqInterface",
    "QutipInterface",
    "QuimbInterface",
    "AVAILABLE_SIMULATORS",
]
