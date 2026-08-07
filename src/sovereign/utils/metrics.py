"""SOVEREIGN — lightweight in-process metrics registry.

Thread-safe counters, gauges, and histograms with a Prometheus-style text
export for /api/v1/system/metrics.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Callable


class Metrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._labels: dict[str, dict[str, str]] = {}

    def incr(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        with self._lock:
            self._counters[name] += value
            if labels:
                self._labels[name] = labels

    def set_gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = float(value)

    def observe(self, name: str, value: float) -> None:
        with self._lock:
            self._histograms[name].append(float(value))
            if len(self._histograms[name]) > 10_000:
                self._histograms[name] = self._histograms[name][-5_000:]

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {"count": len(v), "sum": round(sum(v), 4),
                        "avg": round(sum(v) / len(v), 4) if v else 0.0}
                    for k, v in self._histograms.items()
                },
            }

    def export_prometheus(self) -> str:
        lines: list[str] = []
        for name, value in self._counters.items():
            lines.append(f"# TYPE sovereign_{name} counter")
            lines.append(f"sovereign_{name} {value}")
        for name, value in self._gauges.items():
            lines.append(f"# TYPE sovereign_{name} gauge")
            lines.append(f"sovereign_{name} {value}")
        for name, h in self._histograms.items():
            lines.append(f"# TYPE sovereign_{name}_seconds summary")
            lines.append(f"sovereign_{name}_seconds_count {len(h)}")
            lines.append(f"sovereign_{name}_seconds_sum {sum(h):.4f}")
        return "\n".join(lines) + "\n"


METRICS = Metrics()


def timed(name: str) -> Callable:
    """Decorator: record call duration into the metrics registry."""

    def deco(fn: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = fn(*args, **kwargs)
                METRICS.incr(f"{name}_calls", labels={"result": "ok"})
                return result
            except Exception:
                METRICS.incr(f"{name}_calls", labels={"result": "error"})
                raise
            finally:
                METRICS.observe(f"{name}_seconds", time.perf_counter() - start)

        return wrapper

    return deco
