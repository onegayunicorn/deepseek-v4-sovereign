from dataclasses import dataclass
from typing import List, Optional

@dataclass
class BiometricSample:
    timestamp_ns: int
    heart_rate_bpm: float
    hrv_ms: float
    eeg_bands: dict
    ppg_waveform: List[float]
    motion_xyz: tuple
    skin_temp_c: float
    device_id: str

class UniversalDriver:
    def __init__(self, event_bus):
        self.bus = event_bus
        self.drivers = {
            "sovereign_ring": "BLEArduinoDriver",
            "sovereign_buds": "MuseBciDriver"
        }
        
    def stream_all_biometrics(self):
        # Stream sensors to event bus
        pass
