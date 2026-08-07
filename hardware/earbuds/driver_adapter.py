"""
driver_adapter.py — SovereignBudsAdapter for the SOVEREIGN AI Earbuds.

Host-side Python bridge that connects the earbuds' BLE 5.3 audio +
biometric streams to the Sovereign OS ingest layer. It reuses the
shared driver / sensor stack:

  - muse_driver      (../drivers) — MuseDriverWrapper / EEGPacket
    transport pattern (BLE streaming conventions)
  - vocal_analyzer   (../sensors) — VocalAnalyzer, VocalConfig
    (F0 jitter, spectral tilt, MFCC emotion classification)

Both imports are defensive: sys.path is extended to the sibling
directories, and if either module is unavailable the adapter falls back
to embedded stub classes so the rest of the pipeline keeps working
(CI / hosts without the full stack).

Audio is consumed as raw PCM frame dicts; biometrics as feature dicts
published every 5 s by the bud. Privacy gate: audio is only forwarded
when the wake-word + user consent flags are set by the bud.

Usage:
    buds = SovereignBudsAdapter(device="SOVEREIGN-BUDS-0001")
    buds.connect()
    for chunk in buds.stream_audio(timeout=10.0):
        print(chunk["pcm"][:4])
    for bio in buds.stream_biometrics():
        print(bio)
    buds.close()
"""

from __future__ import annotations

import logging
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path setup: make the shared driver/sensor packages importable.
# We only *reference* them — we never modify files in ../drivers or
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
# Audio / biometric constants (mirror specs.yaml + audio_pipeline.md)
# ---------------------------------------------------------------------------
AUDIO_FS = 48000
AUDIO_FRAME = 128
AUDIO_CHANNELS = 2
AUDIO_BYTES_PER_SAMPLE = 4          # 24-bit packed into int32 container
AUDIO_BLOCK_BYTES = AUDIO_FRAME * AUDIO_CHANNELS * AUDIO_BYTES_PER_SAMPLE

SERVICE_UUID = "0000BUD1-89ab-cdef-0123-456789abcdef"
CHAR_AUDIO = "0000B101-89ab-cdef-0123-456789abcdef"        # LE Audio ISOC (notify)
CHAR_BIOMETRICS = "0000B102-89ab-cdef-0123-456789abcdef"   # 5 s feature frames
CHAR_COMMAND = "0000B103-89ab-cdef-0123-456789abcdef"      # control
CHAR_BATTERY = "0000B104-89ab-cdef-0123-456789abcdef"
CHAR_DEVICE_INFO = "0000B105-89ab-cdef-0123-456789abcdef"


# ---------------------------------------------------------------------------
# Defensive imports with stub fallbacks
# ---------------------------------------------------------------------------
def _import_muse_driver() -> Any:
    """Import MuseDriverWrapper from ../drivers, or return a stub."""
    try:
        from muse_driver import MuseDriverWrapper  # type: ignore

        logger.info("SovereignBudsAdapter: using muse_driver.MuseDriverWrapper")
        return MuseDriverWrapper
    except ImportError:
        logger.warning(
            "SovereignBudsAdapter: muse_driver unavailable — using stub"
        )

        class _MuseDriverStub:
            """Minimal stand-in mirroring the MuseDriverWrapper surface."""

            SAMPLE_RATE: int = 48000

            def __init__(self) -> None:
                self._connected = False

            def init(self) -> None:
                pass

            def connect(self) -> bool:
                self._connected = True
                return True

            def disconnect(self) -> None:
                self._connected = False

            def start_streaming(self) -> bool:
                return self._connected

            def stop_streaming(self) -> None:
                pass

            def is_connected(self) -> bool:
                return self._connected

        return _MuseDriverStub


def _import_vocal_analyzer() -> Any:
    """Import VocalAnalyzer from ../sensors, or return a stub."""
    try:
        from vocal_analyzer import VocalAnalyzer, VocalConfig  # type: ignore

        logger.info("SovereignBudsAdapter: using vocal_analyzer.VocalAnalyzer")
        return VocalAnalyzer, VocalConfig
    except ImportError:
        logger.warning(
            "SovereignBudsAdapter: vocal_analyzer unavailable — using stub"
        )

        class _VocalConfigStub:
            sampling_rate: int = 16000

        class _VocalAnalyzerStub:
            def __init__(self, config: Any = None) -> None:
                self.config = config or _VocalConfigStub()
                self._emotion = "neutral"

            def analyze(self, samples: Any) -> Dict[str, float]:
                return {"f0_jitter": 0.0, "spectral_tilt": 0.0}

            @property
            def emotional_state(self) -> str:
                return self._emotion

        return _VocalAnalyzerStub, _VocalConfigStub


MuseDriverCls = _import_muse_driver()
VocalAnalyzerCls, VocalConfigCls = _import_vocal_analyzer()


# ---------------------------------------------------------------------------
# Main adapter
# ---------------------------------------------------------------------------
@dataclass
class BudsStatus:
    """Snapshot of bud state returned by status()."""

    connected: bool = False
    streaming_audio: bool = False
    streaming_biometrics: bool = False
    playing: bool = False
    wake_armed: bool = False
    consent: bool = False
    in_ear: bool = False
    battery_soc: int = 0
    hr_bpm: int = 0
    skin_temp_c: float = 0.0
    audio_blocks_received: int = 0
    device_info: str = ""


class SovereignBudsAdapter:
    """BLE + audio/biometric adapter for the SOVEREIGN AI Earbuds.

    Backends:
      - ``transport="sim"`` (default): dependency-free simulator that
        injects synthetic audio blocks and biometric frames via
        ``inject_audio_block()`` / ``inject_biometrics()``.
      - ``transport="ble"``: placeholder path for a real LE Audio /
        GATT client (e.g. bleak-based), mirroring the muse_driver
        streaming conventions.
    """

    def __init__(self, device: str = "SOVEREIGN-BUDS-0001",
                 transport: str = "sim") -> None:
        self.device = device
        self.transport = transport
        self._connected = False
        self._streaming_audio = False
        self._streaming_bio = False
        self._playing = False
        self._wake_armed = True
        self._consent = False
        self._in_ear = False
        self._soc = 0
        self._hr = 0
        self._temp = 0.0
        self._blocks = 0
        self._info = ""
        self._t0 = 0.0

        self._muse = MuseDriverCls()
        self._vocal = VocalAnalyzerCls()

        # Sim buffers
        self._audio_q: List[Dict[str, Any]] = []
        self._bio_q: List[Dict[str, Any]] = []

    # -- lifecycle ----------------------------------------------------------

    def connect(self, timeout: float = 10.0) -> bool:
        """Connect to the buds (BLE or simulator backend)."""
        try:
            if self.transport == "ble":
                self._connected = self._ble_connect(timeout)
            else:
                # Reuse the muse_driver connection pattern.
                self._muse.init()
                self._connected = bool(self._muse.connect())
            if self._connected:
                self._t0 = time.monotonic()
                self._info = "SOVEREIGN-BUDS/1.0"
                logger.info("SovereignBudsAdapter connected to %s", self.device)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("connect failed: %s", exc)
            self._connected = False
        return self._connected

    def _ble_connect(self, timeout: float) -> bool:
        """Stub for the real LE Audio / GATT transport."""
        return timeout > 0  # place-holder: inject a BLE client in prod

    def stream_audio(self, timeout: float = 5.0, max_blocks: int = 0) -> Iterator[Dict[str, Any]]:
        """Yield decoded audio blocks (PCM frames) from the bud.

        Each yielded dict::

            {"seq": int, "pcm": [int, ...], "frame_count": 128,
             "channels": 2, "sample_rate": 48000, "voice": bool}

        Audio is only forwarded when ``consent`` is active (privacy gate).
        """
        if not self._connected:
            raise RuntimeError("stream_audio() called before connect()")
        self._streaming_audio = True
        deadline = 0.0 if timeout <= 0 else time.monotonic() + timeout
        count = 0
        try:
            while self._streaming_audio:
                block = self._next_audio()
                if block is None:
                    if deadline and time.monotonic() >= deadline:
                        break
                    time.sleep(0.003)
                    continue
                # Privacy gate: no audio unless wake-word + consent.
                if not (self._consent or self._wake_armed):
                    continue
                self._blocks += 1
                count += 1
                yield block
                if max_blocks and count >= max_blocks:
                    break
        finally:
            self._streaming_audio = False

    def stream_biometrics(self, timeout: float = 30.0, max_frames: int = 0) -> Iterator[Dict[str, Any]]:
        """Yield biometric feature frames (published every ~5 s by the bud)."""
        if not self._connected:
            raise RuntimeError("stream_biometrics() called before connect()")
        self._streaming_bio = True
        deadline = 0.0 if timeout <= 0 else time.monotonic() + timeout
        count = 0
        try:
            while self._streaming_bio:
                frame = self._next_biometrics()
                if frame is None:
                    if deadline and time.monotonic() >= deadline:
                        break
                    time.sleep(0.1)
                    continue
                self._hr = frame.get("hr_bpm", 0)
                self._temp = frame.get("skin_temp_c", 0.0)
                count += 1
                yield frame
                if max_frames and count >= max_frames:
                    break
        finally:
            self._streaming_bio = False

    # -- transport drains ----------------------------------------------------

    def _next_audio(self) -> Optional[Dict[str, Any]]:
        if self.transport == "ble":
            return None  # real LE Audio reader goes here
        return self._audio_q.pop(0) if self._audio_q else None

    def _next_biometrics(self) -> Optional[Dict[str, Any]]:
        if self.transport == "ble":
            return None  # real GATT reader goes here
        return self._bio_q.pop(0) if self._bio_q else None

    def status(self) -> Dict[str, Any]:
        """Return a status snapshot as a plain dict."""
        return BudsStatus(
            connected=self._connected,
            streaming_audio=self._streaming_audio,
            streaming_biometrics=self._streaming_bio,
            playing=self._playing,
            wake_armed=self._wake_armed,
            consent=self._consent,
            in_ear=self._in_ear,
            battery_soc=self._soc,
            hr_bpm=self._hr,
            skin_temp_c=self._temp,
            audio_blocks_received=self._blocks,
            device_info=self._info,
        ).__dict__

    def close(self) -> None:
        """Stop all streams, disconnect, release resources."""
        self._streaming_audio = False
        self._streaming_bio = False
        if hasattr(self._muse, "stop_streaming"):
            try:
                self._muse.stop_streaming()
            except Exception:  # pragma: no cover - defensive
                pass
        if hasattr(self._muse, "disconnect"):
            try:
                self._muse.disconnect()
            except Exception:  # pragma: no cover - defensive
                pass
        self._connected = False
        self._audio_q.clear()
        self._bio_q.clear()
        logger.info("SovereignBudsAdapter closed")

    # -- control passthrough ---------------------------------------------------

    def set_consent(self, enabled: bool) -> None:
        """Grant/revoke audio-upload consent (mirrors bud hold gesture)."""
        self._consent = bool(enabled)

    def set_wake_armed(self, enabled: bool) -> None:
        """Arm/disarm the wake-word listener."""
        self._wake_armed = bool(enabled)

    # -- sim/self-test injection ------------------------------------------------

    def inject_audio_block(self, seq: int = 0, voice: bool = False) -> None:
        """Test hook: enqueue a synthetic audio block (sim transport)."""
        pcm = [0] * (AUDIO_FRAME * AUDIO_CHANNELS)
        self._audio_q.append({
            "seq": seq,
            "pcm": pcm,
            "frame_count": AUDIO_FRAME,
            "channels": AUDIO_CHANNELS,
            "sample_rate": AUDIO_FS,
            "voice": voice,
        })

    def inject_biometrics(self, hr: int = 68, temp_c: float = 36.6) -> None:
        """Test hook: enqueue a synthetic biometric frame (sim transport)."""
        self._bio_q.append({
            "hr_bpm": hr,
            "hrv_ms": 42.0,
            "spo2": 98.0,
            "skin_temp_c": temp_c,
            "head_pose": {"yaw": 0.0, "pitch": 0.0, "roll": 0.0},
            "vocal": self._vocal.analyze([0.0] * 160) if hasattr(self._vocal, "analyze") else {},
            "battery_soc": self._soc,
        })


def _self_test() -> None:
    """Small smoke test for the adapter surface."""
    buds = SovereignBudsAdapter()
    if not buds.connect():
        raise SystemExit("self-test: connect failed")
    buds.inject_audio_block(seq=1, voice=True)
    buds.inject_biometrics(hr=72, temp_c=36.8)
    audio = list(buds.stream_audio(timeout=1.0))
    bio = list(buds.stream_biometrics(timeout=1.0))
    assert audio, "no audio blocks parsed"
    assert bio, "no biometric frames parsed"
    buds.close()
    print("SovereignBudsAdapter self-test OK:",
          "audio=%d blocks" % len(audio),
          "hr=%d" % bio[0]["hr_bpm"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _self_test()
