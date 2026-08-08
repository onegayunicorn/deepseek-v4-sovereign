"""
Post-Load Hook — setup after model load
"""

import time
from typing import Dict, Any


class PostLoadHook:
    """Report model readiness and record load metrics."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.load_seconds = config.get("load_seconds", 0.0)
        self.quant = config.get("quant", "Q4_K_M")

    def run(self) -> Dict[str, Any]:
        print("✅ Model loaded — post-load setup")
        metrics = {
            "model": "gemma-3-12b-it-jailbreak",
            "quant": self.quant,
            "load_seconds": round(self.load_seconds, 2),
            "status": "ready",
            "ready_at": time.time(),
        }
        print(f"   quant={self.quant} · load={metrics['load_seconds']}s · status=ready")
        return metrics


# Hook registration
def post_load_hook(config: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point for post-load hook."""
    return PostLoadHook(config).run()
