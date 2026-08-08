"""Basic inference-path tests (no real model required)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))
MOD = ROOT / "models" / "gemma-3-12b-it-jailbreak"


def test_model_loader_backend_detection():
    import inference.model_loader as ml

    res = ml.load(quant="Q4_K_M", backend="ollama")
    assert res.ok
    assert "ollama" in res.command
    assert res.backend == "ollama"


def test_model_loader_missing_gguf_warns():
    import inference.model_loader as ml

    # force transformers path with no asset present
    res = ml.load(quant="Q4_K_M", backend="transformers")
    assert res.backend == "transformers"
    # message should guide the user (either ok or instructive)
    assert res.message


def test_benchmark_dry_run():
    import tasks.benchmark as bm

    res = bm.benchmark("Q4_K_M", dry_run=True)
    assert res["status"] == "planned"
    assert res["quant"] == "Q4_K_M"


def test_fine_tune_without_dataset_skips():
    import tasks.fine_tune as ft

    res = ft.fine_tune()
    assert res["status"] == "skipped"
    assert "dataset" in res["reason"]
