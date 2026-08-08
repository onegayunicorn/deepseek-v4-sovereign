"""Unit tests for the neural module (PDF Phase 5.1)."""

from __future__ import annotations

import unittest

from neural.bci_v95.interface import bci
from quantum.simulators import QutipInterface


class TestNeural(unittest.TestCase):
    def test_bci_interface(self) -> None:
        bci.initialize()
        self.assertTrue(bci.is_locked())
        self.assertEqual(bci.carrier_hz, 432)

    def test_photonic_grid(self) -> None:
        qutip = QutipInterface()
        state = qutip.density_matrix([1.0, 0.0, 0.0, 1.0])
        self.assertEqual(state.shape, (4, 4))
        # Entangled Bell state has non-zero concurrence.
        self.assertGreater(qutip.concurrence([1.0, 0.0, 0.0, 1.0]), 0.9)


if __name__ == "__main__":
    unittest.main()
