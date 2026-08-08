"""
On-Quantization Hook — record quantization changes and validate the
target quant against the preset table.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import time


class OnQuantizationHook:
    """Instrument quant switches (e.g. Q4_K_M → Q5_K_M)."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.previous_quant = config.get("previous_quant")
        self.new_quant = config.get("new_quant", "Q4_K_M")

    def validate(self) -> bool:
        presets = Path("models/gemma-3-12b-it-jailbreak/config/quantization_presets.yaml")
        if not presets.exists():
            print("⚠️  Quant table not found — skipping validation")
            return True
        import yaml
        with open(presets) as f:
            data = yaml.safe_load(f)
        ids = {v["id"] for v in data.get("variants", [])}
        ok = self.new_quant in ids
        print(f"✅ Quant valid: {self.new_quant}" if ok else f"❌ Unknown quant: {self.new_quant}")
        return ok

    def record(self) -> Dict[str, Any]:
        return {
            "event": "quant.changed",
            "previous_quant": self.previous_quant,
            "new_quant": self.new_quant,
            "timestamp": time.time(),
        }


# Hook registration
def on_quantization_hook(config: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point for quantization hook."""
    hook = OnQuantizationHook(config)
    hook.validate()
    return hook.record()
