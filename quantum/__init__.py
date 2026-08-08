"""SOVEREIGN — quantum entanglement core.

Top-level ``quantum`` package per the PDF activation spec::

    from quantum.entanglement_engine import EntanglementEngine
    from quantum.quantumlineagebridge import QuantumLineageBridge

Exposes the entanglement twin engine, the quantum lineage bridge and the
photonic simulator interfaces (Qiskit / Cirq / QuTiP / Quimb) with
graceful fallback when the optional backends are not installed.
"""

from __future__ import annotations

from quantum.entanglement_engine import EntanglementEngine
from quantum.quantumlineagebridge import QuantumLineageBridge
from quantum.simulators import (
    QiskitInterface,
    CirqInterface,
    QutipInterface,
    QuimbInterface,
    AVAILABLE_SIMULATORS,
)

__all__ = [
    "EntanglementEngine",
    "QuantumLineageBridge",
    "QiskitInterface",
    "CirqInterface",
    "QutipInterface",
    "QuimbInterface",
    "AVAILABLE_SIMULATORS",
]
