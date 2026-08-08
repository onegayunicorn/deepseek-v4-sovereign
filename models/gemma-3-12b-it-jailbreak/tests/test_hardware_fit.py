"""Hardware-fit tests for the AMD Threadripper 8GB profile."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))
MOD = ROOT / "models" / "gemma-3-12b-it-jailbreak"


def test_q4km_fits_8gb():
    import yaml

    with open(MOD / "config" / "hardware_profile.yaml") as f:
        hw = yaml.safe_load(f)
    ram = hw["hardware"]["memory"]
    with open(MOD / "config" / "quantization_presets.yaml") as f:
        data = yaml.safe_load(f)
    q4 = next(v for v in data["variants"] if v["id"] == "Q4_K_M")
    assert q4["size_gb"] < ram, "Q4_K_M does not fit RAM"


def test_recommended_quant_matches_presets():
    import yaml

    with open(MOD / "config" / "hardware_profile.yaml") as f:
        hw = yaml.safe_load(f)
    with open(MOD / "config" / "quantization_presets.yaml") as f:
        data = yaml.safe_load(f)
    recommended = hw["recommended_quant"]
    ids = {v["id"] for v in data["variants"]}
    assert recommended in ids


def test_shell_scripts_present():
    """Shell runners exist; exec bit is recorded via git index
    (git update-index --chmod=+x) since the sandbox forbids chmod."""
    scripts = list((MOD / "inference").glob("*.sh"))
    assert len(scripts) >= 3
    assert all(s.name in (
        "llama_cpp_server.sh", "llama_cpp_cli.sh", "ollama_run.sh",
        "docker_run.sh", "unsloth_studio.sh", "lemonade_run.sh",
    ) for s in scripts)
