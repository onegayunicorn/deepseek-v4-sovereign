"""
Pre-Load Hook — Validation before model load
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

class PreLoadHook:
    """Validate system and model before loading."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_path = Path(config.get("model_path", "models/gemma-3-12b-it-jailbreak/assets/recommended/"))
        self.quant = config.get("quant", "Q4_K_M")
        self.ram_gb = config.get("ram_gb", 8)

    def validate(self) -> bool:
        """Run all pre-load validations."""
        print("🔍 Running pre-load validations...")

        checks = [
            self._check_model_file(),
            self._check_memory(),
            self._check_quant(),
            self._check_dependencies(),
        ]

        return all(checks)

    def _check_model_file(self) -> bool:
        """Check if model file exists."""
        model_file = self.model_path / f"gemma-3-12b-{self.quant}.gguf"
        if not model_file.exists():
            print(f"❌ Model file not found: {model_file}")
            return False
        print(f"✅ Model file found: {model_file} ({model_file.stat().st_size / 1e9:.1f} GB)")
        return True

    def _check_memory(self) -> bool:
        """Check if enough RAM available."""
        try:
            import psutil
        except ImportError:
            print("⚠️  psutil not installed — skipping memory check")
            return True
        available_gb = psutil.virtual_memory().available / 1e9
        required_gb = self.config.get("required_gb", 7.3)

        if available_gb < required_gb:
            print(f"⚠️  Low memory: {available_gb:.1f} GB available, {required_gb:.1f} GB required")
            return False
        print(f"✅ Memory OK: {available_gb:.1f} GB available")
        return True

    def _check_quant(self) -> bool:
        """Check if quant is supported."""
        supported = ["IQ1_S", "IQ1_M", "IQ2_XXS", "IQ2_XS", "IQ2_S", "Q2_K_S", "IQ2_M", "Q2_K",
                     "IQ3_XXS", "IQ3_XS", "IQ3_S", "Q3_K_S", "IQ3_M", "Q3_K_M", "Q3_K_L",
                     "IQ4_XS", "IQ4_NL", "Q4_0", "Q4_K_S", "Q4_K_M", "Q4_1",
                     "Q5_K_S", "Q5_K_M", "Q6_K"]

        if self.quant not in supported:
            print(f"⚠️  Unsupported quant: {self.quant}")
            return False
        print(f"✅ Quant supported: {self.quant}")
        return True

    def _check_dependencies(self) -> bool:
        """Check if all dependencies are installed."""
        try:
            import transformers
            import torch
            import huggingface_hub
            print("✅ Dependencies OK")
            return True
        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
            return False


# Hook registration
def pre_load_hook(config: Dict[str, Any]) -> bool:
    """Entry point for pre-load hook."""
    hook = PreLoadHook(config)
    return hook.validate()
