"""PERO freezer laser source — physical anchor of the closed loop.

PDF API (used by ``sovereign.quantum_closed_loop``)::

    laser = CryoLaser(temperature_c=-20, wavelengths=[450, 532, 633])
    photons = laser.fire(power_mw=150)
    laser.tune(wavelength_nm=532, power_mw=150, temperature_c=-20)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

SUPPORTED_WAVELENGTHS = [405, 450, 532, 633, 780, 1064]
MAX_POWER_MW = {405: 1000, 450: 2000, 532: 500, 633: 300, 780: 200, 1064: 100}


@dataclass
class CryoLaser:
    """Freezer-mounted laser source (simulated photon stream)."""

    temperature_c: float = -20.0
    wavelengths: List[float] = field(default_factory=lambda: [450.0, 532.0, 633.0])
    current_wavelength: float = 450.0
    power_mw: float = 150.0
    active: bool = False

    def __post_init__(self) -> None:
        if self.wavelengths:
            self.current_wavelength = float(self.wavelengths[0])

    def fire(self, power_mw: Optional[float] = None) -> np.ndarray:
        """Generate a photon stream (deterministic base + noise)."""
        if power_mw is not None:
            self.power_mw = float(power_mw)
        self.active = True
        rng = np.random.default_rng(int(self.current_wavelength) + int(self.power_mw))
        photons = rng.standard_normal(1000) * self.power_mw / 100.0
        return photons

    def tune(self, wavelength_nm: float, power_mw: float, temperature_c: float) -> None:
        """Tune laser parameters from model feedback."""
        self.current_wavelength = float(wavelength_nm)
        self.power_mw = float(power_mw)
        self.temperature_c = float(temperature_c)

    def summary(self) -> dict:
        return {
            "wavelength_nm": self.current_wavelength,
            "power_mw": self.power_mw,
            "temperature_c": self.temperature_c,
            "active": self.active,
        }
