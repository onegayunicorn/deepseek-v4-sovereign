"""Import + module structure tests."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))
MOD = ROOT / "models" / "gemma-3-12b-it-jailbreak"


def test_module_layout():
    required = [
        "README.md", "MODEL_SPECS.md", "QUANTIZATION_TABLE.md",
        "config/quantization_presets.yaml", "config/model_config.yaml",
        "config/hardware_profile.yaml", "config/inference_config.yaml",
        "inference/model_loader.py", "inference/transformers.py",
        "hooks/pre_load.py", "hooks/post_load.py", "hooks/on_inference.py",
        "hooks/on_quantization.py",
        "tasks/download_model.py", "tasks/quant_selector.py",
        "tasks/benchmark.py", "tasks/fine_tune.py",
        "triggers/on_model_load.yaml", "triggers/on_inference_complete.yaml",
        "triggers/on_quant_change.yaml",
    ]
    missing = [r for r in required if not (MOD / r).exists()]
    assert not missing, f"missing files: {missing}"


def test_inference_scripts():
    scripts = list((MOD / "inference").glob("*.sh"))
    assert len(scripts) >= 3, f"expected >=3 shell runners, got {len(scripts)}"


def test_hooks_importable():
    import hooks.pre_load, hooks.post_load, hooks.on_inference, hooks.on_quantization  # noqa: F401


def test_tasks_importable():
    import tasks.download_model, tasks.quant_selector, tasks.benchmark, tasks.fine_tune  # noqa: F401
