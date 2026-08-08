"""Universal Driver — hardware abstraction layer (PDF Phase 4.1).

    from hardware.universal_driver import UniversalDriver
    driver = UniversalDriver()
    driver.initialize()
    driver.connect('Sovereign Ring')
    driver.start_streaming()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

SUPPORTED_DEVICES = [
    "Sovereign Ring",
    "Sovereign Buds",
    "BCI v9.5",
    "Samsung A17",
    "Tesla Nexus",
]


@dataclass
class HardwareDevice:
    name: str
    connected: bool = False
    streaming: bool = False


class UniversalDriver:
    """Hardware abstraction over the sovereign device bus."""

    def __init__(self) -> None:
        self.initialized = False
        self.devices: List[HardwareDevice] = []

    def initialize(self) -> "UniversalDriver":
        self.devices = [HardwareDevice(name=name) for name in SUPPORTED_DEVICES]
        self.initialized = True
        return self

    def connect(self, device_name: str) -> HardwareDevice:
        for device in self.devices:
            if device.name == device_name:
                device.connected = True
                return device
        raise ValueError(f"Unknown device: {device_name}")

    def start_streaming(self) -> None:
        for device in self.devices:
            if device.connected:
                device.streaming = True

    def connected_count(self) -> int:
        return sum(1 for d in self.devices if d.connected)

    def summary(self) -> Dict[str, object]:
        return {
            "initialized": self.initialized,
            "devices": [d.name for d in self.devices],
            "connected": self.connected_count(),
            "streaming": sum(1 for d in self.devices if d.streaming),
        }
