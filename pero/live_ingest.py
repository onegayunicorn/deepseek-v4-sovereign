"""PERO freezer-laser live ingest.

Reads video frames → extracts laser intensity → computes SPDC metrics →
streams to listeners → model suggests tuning → writes back to laser params.

Graceful degradation: without opencv or a video file, a synthetic frame
generator keeps the loop running so the pipeline is testable end-to-end.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import AsyncIterator, Callable, Optional

import numpy as np

try:  # pragma: no cover - optional dependency
    import cv2
except Exception:  # pragma: no cover
    cv2 = None

BASELINE_EFFICIENCY = 0.5214
BASELINE_COHERENCE = 0.6466

CRYSTAL_RESPONSE = {
    "BBO":     {"gain": 1.21, "temp_opt": -21.0},
    "KTP":     {"gain": 1.15, "temp_opt": -19.5},
    "LiNbO3":  {"gain": 1.09, "temp_opt": -22.0},
    "Quartz":  {"gain": 1.04, "temp_opt": -18.0},
    "Amethyst": {"gain": 1.02, "temp_opt": -20.0},
}

DEFAULT_VIDEO = "data/raw/videos/20260807_223101.mp4"


@dataclass
class LaserFrame:
    """One frame of photonic telemetry."""

    t: float
    wavelength_nm: int
    power_mw: float
    temperature_c: float
    crystal: str
    intensity_mean: float
    intensity_std: float
    splitting_efficiency: float
    spatial_coherence: float
    bell_fidelity: float
    pairs_this_frame: int


class LiveIngest:
    """Streams LaserFrame metrics from a video source or synthetic frames."""

    def __init__(
        self,
        video_source: Optional[str] = None,
        crystal: str = "BBO",
        wavelength_nm: int = 532,
    ) -> None:
        self.video_source = video_source
        self.crystal = crystal
        self.wavelength_nm = wavelength_nm
        self.temperature_c = CRYSTAL_RESPONSE[crystal]["temp_opt"]
        self.power_mw = 150.0
        self.frame_num = 0
        self.pairs_total = 0
        self.synthetic = video_source is None
        self._cap = None
        self._listeners: list[Callable[[LaserFrame], object]] = []

    # ── lifecycle ──────────────────────────────────────────────────────
    def open(self) -> None:
        if self.synthetic:
            return  # synthetic mode: no device needed
        if cv2 is None:
            raise RuntimeError("opencv-python required for video ingest (or pass no source)")
        self._cap = cv2.VideoCapture(self.video_source)
        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {self.video_source}")

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def __enter__(self) -> "LiveIngest":
        self.open()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ── metrics ────────────────────────────────────────────────────────
    def _metrics_from_frame(self, frame: np.ndarray) -> LaserFrame:
        if cv2 is not None and frame.ndim == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        elif frame.ndim == 3:
            gray = frame.mean(axis=2)  # numpy fallback (no opencv)
        else:
            gray = frame
        mean = float(gray.mean()) / 255.0
        std = float(gray.std()) / 255.0
        resp = CRYSTAL_RESPONSE[self.crystal]
        # Cryo-suppressed phonon noise → higher efficiency + coherence
        temp_factor = 1.0 - abs(self.temperature_c - resp["temp_opt"]) * 0.008
        eff = float(np.clip(BASELINE_EFFICIENCY * resp["gain"] * (0.9 + 0.2 * mean) * temp_factor, 0.3, 0.75))
        coh = float(np.clip(BASELINE_COHERENCE * resp["gain"] * (1.0 - 0.6 * std) * temp_factor, 0.4, 0.92))
        fid = float(np.clip(0.97 + 0.035 * (eff * coh) ** 0.5, 0.95, 0.9999))
        pairs = max(1, int(24 * eff * coh * resp["gain"]))
        self.pairs_total += pairs
        self.frame_num += 1
        return LaserFrame(
            t=time.time(),
            wavelength_nm=self.wavelength_nm,
            power_mw=self.power_mw,
            temperature_c=self.temperature_c,
            crystal=self.crystal,
            intensity_mean=mean,
            intensity_std=std,
            splitting_efficiency=eff,
            spatial_coherence=coh,
            bell_fidelity=fid,
            pairs_this_frame=pairs,
        )

    def _synthetic_frame(self) -> np.ndarray:
        """Deterministic synthetic frame ~ real video statistics."""
        rng = np.random.default_rng(self.frame_num)
        base = 60.0 + 40.0 * np.sin(self.frame_num / 10.0)
        return rng.normal(base, 24.0, size=(240, 320, 3)).clip(0, 255).astype("uint8")

    # ── streaming ──────────────────────────────────────────────────────
    async def stream(self, fps: int = 10) -> AsyncIterator[LaserFrame]:
        loop = asyncio.get_event_loop()
        interval = 1.0 / fps
        while True:
            t0 = loop.time()
            if self.synthetic:
                frame = self._synthetic_frame()
            else:
                ok, frame = await loop.run_in_executor(None, self._cap.read)
                if not ok:
                    break
            m = self._metrics_from_frame(frame)
            for fn in self._listeners:
                try:
                    await fn(m)
                except Exception:
                    pass
            yield m
            dt = loop.time() - t0
            if dt < interval:
                await asyncio.sleep(interval - dt)

    def on_frame(self, fn: Callable[[LaserFrame], object]) -> None:
        self._listeners.append(fn)

    def tune(
        self,
        *,
        power_mw: Optional[float] = None,
        temperature_c: Optional[float] = None,
        wavelength_nm: Optional[int] = None,
    ) -> None:
        if power_mw is not None:
            self.power_mw = float(np.clip(power_mw, 10, 500))
        if temperature_c is not None:
            self.temperature_c = float(np.clip(temperature_c, -30, 10))
        if wavelength_nm is not None:
            self.wavelength_nm = int(np.clip(wavelength_nm, 380, 1100))


# Singleton per crystal+source
_ingest_cache: dict[str, LiveIngest] = {}


def get_or_create_ingest(source: Optional[str], crystal: str = "BBO", **kw: object) -> LiveIngest:
    key = f"{source or 'synthetic'}:{crystal}"
    if key not in _ingest_cache:
        _ingest_cache[key] = LiveIngest(source, crystal=crystal, **kw)  # type: ignore[arg-type]
    return _ingest_cache[key]
