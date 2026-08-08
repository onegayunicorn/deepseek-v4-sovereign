"""
Quant Selector — Hardware-optimized quantization picker
"""

import yaml
from pathlib import Path

def select_quant(hardware_profile: dict) -> dict:
    """
    Select best quant for hardware.
    """
    ram_gb = hardware_profile.get("ram_gb", 8)
    is_cpu = hardware_profile.get("is_cpu", True)
    use_case = hardware_profile.get("use_case", "balanced")

    # Load quant table
    quant_path = Path("models/gemma-3-12b-it-jailbreak/config/quantization_presets.yaml")
    with open(quant_path) as f:
        quants = yaml.safe_load(f)["variants"]

    # Filter by RAM
    candidates = [q for q in quants if q["size_gb"] < ram_gb * 0.9]

    if not candidates:
        return {"error": "No quant fits in available RAM"}

    # Select based on use case
    if use_case == "speed":
        selected = min(candidates, key=lambda q: q["size_gb"])
    elif use_case == "quality":
        selected = max(candidates, key=lambda q: q["size_gb"])
    else:  # balanced
        # Sort by size, pick middle
        candidates.sort(key=lambda q: q["size_gb"])
        selected = candidates[len(candidates) // 2]

    return {
        "selected": selected,
        "hardware": hardware_profile,
        "candidates": len(candidates),
        "ram_available": ram_gb,
        "ram_used": selected["size_gb"],
        "ram_remaining": ram_gb - selected["size_gb"]
    }

if __name__ == "__main__":
    hardware = {
        "ram_gb": 8,
        "is_cpu": True,
        "use_case": "balanced",
        "cpu": "AMD Ryzen Threadripper Zen 9 5000"
    }
    result = select_quant(hardware)
    print(f"✅ Selected: {result['selected']['id']} ({result['selected']['size_gb']:.2f} GB)")
    print(f"   RAM: {result['ram_used']:.2f}/{result['ram_available']:.2f} GB")
