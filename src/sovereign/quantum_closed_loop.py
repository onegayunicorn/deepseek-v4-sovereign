"""Photonic-quantum self-sustaining closed loop.

PDF spec (Solution 4)::

    from sovereign.quantum_closed_loop import QuantumSovereignLoop
    QuantumSovereignLoop().run_closed_loop()

PERO laser → quantum states → local model inference → laser tuning →
repeat.  Zero external dependencies, zero tokens, zero API calls.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional, Tuple

import numpy as np

from pero.entanglement import SPDCSource
from pero.laser import CryoLaser
from sovereign.biometric import BiometricSession
from sovereign.model import LocalDeepSeek


class QuantumSovereignLoop:
    """Self-sustaining photonic-quantum feedback loop."""

    def __init__(self) -> None:
        self.laser = CryoLaser(temperature_c=-20, wavelengths=[450, 532, 633])
        self.spdc = SPDCSource(crystals=["BBO", "KTP", "LiNbO3"])
        self.model = LocalDeepSeek(model_path="./models/deepseek-v4-flash-0731")
        self.biometric = BiometricSession()
        self.fidelity = 0.999423
        self.entangled_pairs = 847
        self.loop_iteration = 0

    def quantum_feedforward(self) -> Tuple[np.ndarray, float]:
        """Step 1: generate quantum state from the physical laser."""
        photons = self.laser.fire(power_mw=150)
        bell_states = self.spdc.generate_bell_pairs(photons, count=847)
        measured_fidelity = self.spdc.measure_fidelity(bell_states)
        return bell_states, measured_fidelity

    def model_inference(self, quantum_input: np.ndarray) -> Dict[str, Any]:
        """Step 2: local model runs on quantum-processed data."""
        return self.model.generate(
            quantum_context=quantum_input,
            max_tokens=4096,
            temperature=0.7,
        )

    def laser_feedback(self, model_output: Dict[str, Any]) -> None:
        """Step 3: model tunes laser parameters — closed loop."""
        suggestions = self.model.extract_laser_parameters(model_output)
        self.laser.tune(
            wavelength_nm=suggestions.get("wavelength", 532),
            power_mw=suggestions.get("power", 150),
            temperature_c=suggestions.get("temperature", -20),
        )

    def biometric_sync(self) -> bool:
        """Step 4: human-in-loop via biometrics — no passwords."""
        ok, _ = self.biometric.verify_and_route()
        return ok

    def run_once(self) -> Dict[str, Any]:
        """One full loop pass; returns the iteration status."""
        self.loop_iteration += 1
        states, fid = self.quantum_feedforward()
        self.fidelity = fid
        output = self.model_inference(states)
        self.laser_feedback(output)
        return {
            "iteration": self.loop_iteration,
            "fidelity": round(float(fid), 6),
            "pairs": self.entangled_pairs,
            "laser": self.laser.summary(),
        }

    def run_closed_loop(self, iterations: Optional[int] = None, sleep_s: float = 0.0) -> None:
        """Run the self-sustaining loop (bounded when ``iterations`` set)."""
        _purge_credentials()
        count = 0
        while iterations is None or count < iterations:
            count += 1
            if not self.biometric_sync():
                time.sleep(1.0)
                continue
            status = self.run_once()
            if status["iteration"] % 100 == 0:
                print(
                    f"LOOP #{status['iteration']} | F={status['fidelity']:.6f} | "
                    f"pairs={status['pairs']}"
                )
            if sleep_s:
                time.sleep(sleep_s)


def _purge_credentials() -> None:
    for key in list(os.environ.keys()):
        lowered = key.lower()
        if any(s in lowered for s in ("token", "key", "secret", "password", "azure")):
            del os.environ[key]
