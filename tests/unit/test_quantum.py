"""Unit tests for the quantum module (PDF Phase 5.1)."""

from __future__ import annotations

import unittest

from quantum.entanglement_engine import EntanglementEngine
from quantum.quantumlineagebridge import QuantumLineageBridge
from quantum.simulators import (
    CirqInterface,
    QiskitInterface,
    QuimbInterface,
    QutipInterface,
)


class TestQuantum(unittest.TestCase):
    def test_entanglement_pairs(self) -> None:
        engine = EntanglementEngine(num_pairs=847)
        engine.initialize()
        pairs = engine.generate_pairs()
        self.assertEqual(len(pairs), 847)
        self.assertEqual(engine.count(), 847)

    def test_bell_fidelity(self) -> None:
        engine = EntanglementEngine(num_pairs=847, seed=42)
        engine.initialize()
        engine.generate_pairs()
        self.assertGreater(engine.mean_fidelity, 0.9990)

    def test_lineage_bridge(self) -> None:
        bridge = QuantumLineageBridge()
        bridge.initialize()
        n = bridge.anchor_ancestral_generations(12)
        self.assertEqual(n, 12)
        self.assertIsNotNone(bridge.ancestral_tensor)
        self.assertLessEqual(bridge.merged_entries(), 1_000_000)

    def test_simulators(self) -> None:
        qiskit = QiskitInterface()
        pairs = qiskit.generate_bell_pairs(847)
        self.assertEqual(pairs.shape, (847, 4))
        self.assertGreater(qiskit.measure_fidelity(pairs), 0.99)

        cirq = CirqInterface()
        state = cirq.create_photonic_entanglement(pairs)
        self.assertEqual(state["pairs"], 847)

        qutip = QutipInterface()
        self.assertGreaterEqual(qutip.concurrence(pairs[0]), 0.0)
        self.assertGreaterEqual(qutip.entropy(pairs[0]), -1e-6)

        quimb = QuimbInterface()
        self.assertAlmostEqual(quimb.purity(pairs[0]), 1.0, places=3)


if __name__ == "__main__":
    unittest.main()
