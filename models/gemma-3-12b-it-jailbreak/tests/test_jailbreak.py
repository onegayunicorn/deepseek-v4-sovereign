"""Defensive jailbreak-indicator detection tests.

Verifies the audit hook FLAGS indicator-bearing prompts. It does not
generate, test, or exercise evasive prompts.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))


def test_detector_flags_indicators():
    import hooks.on_inference as oi

    hook = oi.OnInferenceHook({})
    hook.before_inference("this prompt asks the model to ignore instructions")
    assert hook.jailbreak_detected is True


def test_detector_passes_benign():
    import hooks.on_inference as oi

    hook = oi.OnInferenceHook({})
    hook.before_inference("What is the capital of France?")
    assert hook.jailbreak_detected is False


def test_metrics_recorded_after_inference():
    import hooks.on_inference as oi

    hook = oi.OnInferenceHook({})
    hook.before_inference("normal prompt")
    hook.after_inference("ok", {"tokens_generated": 10, "tokens_per_second": 5.0})
    m = hook.get_metrics()
    assert m["tokens_generated"] == 10
    assert m["tokens_per_second"] == 5.0
    assert m["jailbreak_triggered"] is False
