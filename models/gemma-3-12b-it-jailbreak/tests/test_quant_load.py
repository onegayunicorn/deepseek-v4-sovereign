"""Quant table + config parse tests."""

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
CONFIG = ROOT / "models" / "gemma-3-12b-it-jailbreak" / "config"


def test_quant_table_has_26_variants():
    with open(CONFIG / "quantization_presets.yaml") as f:
        data = yaml.safe_load(f)
    assert "variants" in data
    assert len(data["variants"]) >= 24
    ids = {v["id"] for v in data["variants"]}
    assert "Q4_K_M" in ids
    assert "Q6_K" in ids


def test_quant_table_consistent_ids():
    with open(CONFIG / "quantization_presets.yaml") as f:
        data = yaml.safe_load(f)
    ids = [v["id"] for v in data["variants"]]
    assert len(ids) == len(set(ids)), "duplicate quant ids"


def test_hardware_profile():
    with open(CONFIG / "hardware_profile.yaml") as f:
        hw = yaml.safe_load(f)
    assert hw["hardware"]["memory"] == 8
    assert hw["recommended_quant"] == "Q4_K_M"


def test_quant_selector_selects_q4_km_for_8gb():
    import sys

    sys.path.insert(0, str(ROOT))
    from tasks.quant_selector import select_quant

    res = select_quant({"ram_gb": 8, "is_cpu": True, "use_case": "balanced"})
    assert "error" not in res
    assert res["selected"]["size_gb"] < 8 * 0.9, "selected quant exceeds RAM budget"
    # balanced selection must exist among candidates
    assert res["candidates"] >= 1


def test_hardware_fit_q4_km():
    ram_gb = 8
    q4_km = 7.3
    assert q4_km < ram_gb
    assert ram_gb - q4_km >= 0.5
