"""Performance benchmark suite (PDF Phase 5.2)."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Dict

# Standalone-run bootstrap: make repo root + src/ importable.
_ROOT = Path(__file__).resolve().parent.parent
for _p in (str(_ROOT), str(_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
os.environ.setdefault("JWT_SECRET", "bench-secret")
os.environ.setdefault("SOVEREIGN_MODE", "test")

from bio.dna.harmonic_resonance import HarmonicResonanceEngine
from bio.dna.kaleidoscope import KaleidoscopeEngine
from bio.genomics.pipeline import GenomicPipeline
from quantum.entanglement_engine import EntanglementEngine
from quantum.quantumlineagebridge import QuantumLineageBridge


class PerformanceSuite:
    """Runs the quantum / neural / genomic / api benchmark groups."""

    def run_quantum_benchmarks(self) -> Dict[str, object]:
        start = time.perf_counter()
        engine = EntanglementEngine(num_pairs=847, seed=42)
        engine.initialize()
        engine.generate_pairs()
        bridge = QuantumLineageBridge()
        bridge.initialize()
        bridge.anchor_ancestral_generations(12)
        elapsed = time.perf_counter() - start
        return {"group": "quantum", "seconds": round(elapsed, 4), "pairs": 847, "ok": True}

    def run_neural_benchmarks(self) -> Dict[str, object]:
        from neural.bci_v95.interface import bci

        start = time.perf_counter()
        bci.initialize()
        elapsed = time.perf_counter() - start
        return {
            "group": "neural",
            "seconds": round(elapsed, 4),
            "carrier_hz": bci.carrier_hz,
            "ok": True,
        }

    def run_genomic_benchmarks(self) -> Dict[str, object]:
        start = time.perf_counter()
        pipeline = GenomicPipeline()
        pipeline.load_reference("GRCh38")
        variants = pipeline.call_variants("sample.fastq")
        resonance = HarmonicResonanceEngine()
        resonance.initialize_strands(10000)
        for _ in range(100):
            resonance.apply_recursive_wave(100)
        kaleido = KaleidoscopeEngine().sweep_all_permutations()
        elapsed = time.perf_counter() - start
        return {
            "group": "genomic",
            "seconds": round(elapsed, 4),
            "variants": len(variants),
            "awakening_pct": round(resonance.current_awakening * 100, 1),
            "kaleidoscope_perms": kaleido["completed"],
            "ok": True,
        }

    def run_api_benchmarks(self) -> Dict[str, object]:
        start = time.perf_counter()
        from sovereign.main import app  # noqa: F401

        elapsed = time.perf_counter() - start
        return {"group": "api", "seconds": round(elapsed, 4), "routes": len(app.routes), "ok": True}

    def run_all(self) -> Dict[str, object]:
        results = [
            self.run_quantum_benchmarks(),
            self.run_neural_benchmarks(),
            self.run_genomic_benchmarks(),
            self.run_api_benchmarks(),
        ]
        return {"groups": results, "all_passed": all(r["ok"] for r in results)}


if __name__ == "__main__":
    suite = PerformanceSuite()
    result = suite.run_all()
    for group in result["groups"]:
        print(group)
    print("All benchmarks passed:", result["all_passed"])
