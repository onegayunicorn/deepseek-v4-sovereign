"""
driver_adapter.py — BciRingAdapter for the SOVEREIGN BCI Ring.

Host-side Python bridge that connects the ring's BLE GATT service to the
Sovereign OS ingest layer. It reuses the shared driver / sensor stack:

  - qlb_arduino_driver (../drivers) — QLB I2C/GPIO bridge (bring-up path)
  - eeg_processor     (../sensors)  — EEGProcessor, EEGConfig (band powers)

Both imports are defensive: sys.path is extended to the sibling
directories, and if either module is unavailable the adapter falls back
to embedded stub classes so the rest of the pipeline keeps working
(useful in CI / on hosts without the full stack).

Protocol: see protocol.md — 20-byte frames:
  [0]=0x53 sync [1]=seq [2]=type [3]=flags [4..17]=payload
  [18..19]=crc16 CCITT-FALSE over bytes 0..17

Usage:
    ring = BciRingAdapter(device="nrf52840-ble")
    ring.connect()
    for pkt in ring.stream(timeout=10.0):
        print(pkt)
    ring.close()
"""

from __future__ import annotations

import logging
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path setup: make the shared driver/sensor packages importable.
# We only *reference* them — we never modify the files in ../drivers or
# ../sensors.
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT = os.path.dirname(os.path.dirname(_HERE))  # .../deepseek-v4-sovereign
_DRIVERS = os.path.join(_PROJECT, "drivers")
_SENSORS = os.path.join(_PROJECT, "sensors")
for _p in (_DRIVERS, _SENSORS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# Protocol constants (mirror protocol.md)
# ---------------------------------------------------------------------------
PKT_SYNC = 0x53
PKT_SIZE = 20
TYPE_EEG = 0x01
TYPE_PPG = 0x02
TYPE_IMU = 0x03
TYPE_INFO = 0x04
FLAG_RAW = 0x80
FLAG_BLOCK_END = 0x40

SERVICE_UUID = "0000SVR1-89ab-cdef-0123-456789abcdef"
CHAR_UUIDS = {
    "eeg_stream": "0000EE01-89ab-cdef-0123-456789abcdef",
    "ppg_stream": "0000EE02-89ab-cdef-0123-456789abcdef",
    "imu_stream": "0000EE03-89ab-cdef-0123-456789abcdef",
    "command": "0000EE04-89ab-cdef-0123-456789abcdef",
    "battery": "0000EE05-89ab-cdef-0123-456789abcdef",
    "device_info": "0000EE06-89ab-cdef-0123-456789abcdef",
}


# ---------------------------------------------------------------------------
# Defensive imports with stub fallbacks
# ---------------------------------------------------------------------------
def _import_qlb_driver() -> Any:
    """Import QLBDriver from ../drivers, or return a stub."""
    try:
        from qlb_arduino_driver import QLBDriver  # type: ignore

        logger.info("BciRingAdapter: using qlb_arduino_driver.QLBDriver")
        return QLBDriver
    except ImportError:
        logger.warning(
            "BciRingAdapter: qlb_arduino_driver unavailable — using stub"
        )

        class _QLBStub:
            """Minimal stand-in so pipeline code still type-checks."""

            def connect(self, device: str) -> bool:
                return True

            def auto_connect(self) -> bool:
                return True

            def disconnect(self) -> None:
                pass

            def is_connected(self) -> bool:
                return False

            def i2c_read(self, dev: int, reg: int, out: list, ln: int) -> bool:
                return True

            def i2c_write(self, dev: int, reg: int, data: bytes) -> bool:
                return True

            def device_info(self, info: list) -> bool:
                info.append("QLB_STUB")
                return True

        return _QLBStub


def _import_eeg_processor() -> Any:
    """Import EEGProcessor from ../sensors, or return a stub."""
    try:
        from eeg_processor import EEGConfig, EEGProcessor  # type: ignore

        logger.info("BciRingAdapter: using eeg_processor.EEGProcessor")
        return EEGProcessor, EEGConfig
    except ImportError:
        logger.warning(
            "BciRingAdapter: eeg_processor unavailable — using stub"
        )

        class _EEGConfigStub:
            sampling_rate: float = 500.0

        class _EEGProcessorStub:
            def __init__(self, config: Any = None) -> None:
                self.config = config or _EEGConfigStub()

            def process(self, samples: Any) -> Dict[str, float]:
                return {"theta": 0.0, "alpha": 0.0, "beta": 0.0, "gamma": 0.0}

        return _EEGProcessorStub, _EEGConfigStub


QLBDriverCls = _import_qlb_driver()
EEGProcessorCls, EEGConfigCls = _import_eeg_processor()


# ---------------------------------------------------------------------------
# Packet parsing helpers
# ---------------------------------------------------------------------------
def _crc16_ccitt(data: bytes) -> int:
    """CRC-16/CCITT-FALSE over the given bytes."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if (crc & 0x8000) else (crc << 1)
        crc &= 0xFFFF
    return crc


def parse_packet(frame: bytes) -> Optional[Dict[str, Any]]:
    """Validate and decode one 20-byte BLE notify frame into a dict.

    Returns None if the frame is malformed or fails CRC.
    """
    if frame is None or len(frame) != PKT_SIZE:
        return None
    if frame[0] != PKT_SYNC:
        return None
    if _crc16_ccitt(frame[:18]) != (frame[18] | (frame[19] << 8)):
        return None

    ptype = frame[2]
    flags = frame[3]
    payload = list(frame[4:18])
    sample_idx = payload[12] | (payload[13] << 8)

    if ptype == TYPE_EEG:
        theta = ((payload[0] << 8) | payload[1]) / 4095.0
        alpha = ((payload[2] << 8) | payload[3]) / 4095.0
        beta = ((payload[4] << 8) | payload[5]) / 4095.0
        gamma = ((payload[6] << 8) | payload[7]) / 4095.0
        return {
            "type": "eeg",
            "seq": frame[1],
            "block_end": bool(flags & FLAG_BLOCK_END),
            "raw": bool(flags & FLAG_RAW),
            "sample_index": sample_idx,
            "theta": theta,
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma,
            "blink_count": payload[8],
            "quality": payload[9],
            "rms_uv": payload[10] | (payload[11] << 8),
        }
    if ptype == TYPE_PPG:
        return {
            "type": "ppg",
            "seq": frame[1],
            "block_end": bool(flags & FLAG_BLOCK_END),
            "sample_index": sample_idx,
            "hr_bpm": (payload[0] | (payload[1] << 8)) / 100.0,
            "hrv_ms": (payload[2] | (payload[3] << 8)) / 100.0,
            "spo2": (payload[4] | (payload[5] << 8)) / 100.0,
            "ir_baseline": int.from_bytes(bytes(payload[6:10]), "little"),
            "confidence": payload[10],
            "quality": payload[11],
        }
    if ptype == TYPE_IMU:
        def _i16(lo: int, hi: int) -> int:
            v = lo | (hi << 8)
            return v - 65536 if v >= 0x8000 else v

        return {
            "type": "imu",
            "seq": frame[1],
            "block_end": bool(flags & FLAG_BLOCK_END),
            "sample_index": sample_idx,
            "accel_mg": (_i16(payload[0], payload[1]),
                         _i16(payload[2], payload[3]),
                         _i16(payload[4], payload[5])),
            "gyro_mdps": (_i16(payload[6], payload[7]),
                          _i16(payload[8], payload[9]),
                          _i16(payload[10], payload[11])),
        }
    if ptype == TYPE_INFO:
        return {"type": "info", "seq": frame[1], "payload": bytes(payload)}
    return {"type": "unknown", "seq": frame[1], "raw": frame.hex()}


# ---------------------------------------------------------------------------
# Main adapter
# ---------------------------------------------------------------------------
@dataclass
class RingStatus:
    """Snapshot of ring state returned by status()."""

    connected: bool = False
    streaming: bool = False
    battery_soc: int = 0
    uptime_s: float = 0.0
    packets_received: int = 0
    crc_errors: int = 0
    raw_opt_in: bool = False
    device_info: str = ""


class BciRingAdapter:
    """BLE + protocol adapter for the SOVEREIGN BCI Ring.

    Wire paths:
      - Real BLE transport (via bleak-style client) is used when
        ``transport == "ble"``; a serial loopback / simulator is used
        for ``transport == "sim"`` (default, dependency-free).
      - The QLB driver and EEGProcessor are referenced for bring-up and
        on-host DSP, mirroring the driver/sensor stack conventions.
    """

    def __init__(self, device: str = "SOVEREIGN-RING-0001",
                 transport: str = "sim") -> None:
        self.device = device
        self.transport = transport
        self._connected = False
        self._streaming = False
        self._packets = 0
        self._crc_errors = 0
        self._raw_opt_in = False
        self._soc = 0
        self._info = ""
        self._t0 = 0.0
        self._qlb = QLBDriverCls()
        self._eeg = EEGProcessorCls()
        # Internal packet queue for sim mode
        self._sim_frames: List[bytes] = []

    # -- lifecycle ----------------------------------------------------------

    def connect(self, timeout: float = 10.0) -> bool:
        """Connect to the ring (BLE or simulator backend)."""
        try:
            if self.transport == "ble":
                # Real path: scan for device, pair, enable notify on
                # eeg/ppg/imu characteristics. Requires a BLE stack
                # (e.g. bleak) — kept abstract here.
                self._connected = self._ble_connect(timeout)
            else:
                # Simulator path: exercise the QLB bridge pattern.
                ok = self._qlb.auto_connect() if hasattr(self._qlb,
                                                         "auto_connect") else False
                self._connected = ok or self._qlb.connect(self.device)
            if self._connected:
                self._t0 = time.monotonic()
                info_list: List[str] = []
                if hasattr(self._qlb, "device_info"):
                    self._qlb.device_info(info_list)
                self._info = info_list[0] if info_list else "SOVEREIGN-RING/1.0"
                logger.info("BciRingAdapter connected to %s", self.device)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("connect failed: %s", exc)
            self._connected = False
        return self._connected

    def _ble_connect(self, timeout: float) -> bool:
        """Stub for the real BLE transport (bleak/gattlib)."""
        return timeout > 0  # place-holder: inject a BLE client in prod

    def stream(self, timeout: float = 5.0, max_packets: int = 0) -> Iterator[Dict[str, Any]]:
        """Yield decoded packet dicts until timeout or max_packets reached.

        Args:
            timeout: seconds to keep yielding (0 = until closed).
            max_packets: optional cap on total packets yielded.

        Yields:
            Packet dicts from parse_packet() — ``type`` in
            {"eeg", "ppg", "imu", "info", "unknown"}.
        """
        if not self._connected:
            raise RuntimeError("stream() called before connect()")
        self._streaming = True
        deadline = 0.0 if timeout <= 0 else time.monotonic() + timeout
        count = 0
        try:
            while self._streaming:
                frame = self._next_frame()
                if frame is None:
                    if deadline and time.monotonic() >= deadline:
                        break
                    time.sleep(0.002)
                    continue
                pkt = parse_packet(frame)
                if pkt is None:
                    self._crc_errors += 1
                    continue
                self._packets += 1
                count += 1
                yield pkt
                if max_packets and count >= max_packets:
                    break
        finally:
            self._streaming = False

    def _next_frame(self) -> Optional[bytes]:
        """Pull one raw 20-byte frame from the active transport."""
        if self.transport == "ble":
            # Real transport: read from the GATT notify queue.
            return None
        # Sim transport: drain the injected frame buffer.
        if self._sim_frames:
            return self._sim_frames.pop(0)
        return None

    def status(self) -> Dict[str, Any]:
        """Return a status snapshot as a plain dict."""
        return RingStatus(
            connected=self._connected,
            streaming=self._streaming,
            battery_soc=self._soc,
            uptime_s=round(time.monotonic() - self._t0, 2) if self._connected else 0.0,
            packets_received=self._packets,
            crc_errors=self._crc_errors,
            raw_opt_in=self._raw_opt_in,
            device_info=self._info,
        ).__dict__

    def close(self) -> None:
        """Stop streaming, disconnect, release resources."""
        self._streaming = False
        if hasattr(self._qlb, "disconnect"):
            try:
                self._qlb.disconnect()
            except Exception:  # pragma: no cover - defensive
                pass
        self._connected = False
        self._sim_frames.clear()
        logger.info("BciRingAdapter closed")

    # -- convenience: sim/self-test injection ---------------------------------

    def inject_frame(self, frame: bytes) -> None:
        """Test hook: inject a raw frame (sim transport) for unit tests."""
        self._sim_frames.append(frame)


def _self_test() -> None:
    """Small smoke test: build + parse a valid EEG frame."""
    ring = BciRingAdapter()
    if not ring.connect():
        raise SystemExit("self-test: connect failed")
    frame = bytes([
        PKT_SYNC, 0x01, TYPE_EEG, FLAG_BLOCK_END,
        0x0F, 0x7F,  # theta 0x0F7F → 3967/4095 ≈ 0.969
        0x08, 0x00,  # alpha 0x0800 → 2048/4095 ≈ 0.500
        0x04, 0x00,  # beta  0x0400 → 1024/4095 ≈ 0.250
        0x02, 0x00,  # gamma 0x0200 → 512/4095  ≈ 0.125
        0x01, 0xC8, 0x00, 0x00, 0x00, 0x00,
    ])
    crc = _crc16_ccitt(frame[:18])
    frame = frame[:18] + bytes([crc & 0xFF, crc >> 8])
    ring.inject_frame(frame)
    packets = list(ring.stream(timeout=1.0))
    assert packets, "no packets parsed"
    assert packets[0]["type"] == "eeg", packets[0]
    ring.close()
    print("BciRingAdapter self-test OK:", packets[0]["alpha"], packets[0]["beta"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _self_test()
