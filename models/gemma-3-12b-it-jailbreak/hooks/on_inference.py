"""
On-Inference Hook — Monitor and enhance inference (defensive: flags
jailbreak-indicator prompts for audit, never amplifies them).
"""

import time
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class InferenceMetrics:
    """Metrics from inference run."""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    tokens_generated: int = 0
    tokens_per_second: float = 0.0
    prompt_tokens: int = 0
    total_tokens: int = 0
    jailbreak_triggered: bool = False
    memory_used_gb: float = 0.0

class OnInferenceHook:
    """Hook for inference monitoring and enhancement."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = InferenceMetrics()
        self.jailbreak_detected = False

    def before_inference(self, prompt: str) -> str:
        """Pre-process prompt before inference."""
        print(f"🔮 Inference started: {len(prompt)} chars")

        # Detect jailbreak attempts (defensive audit)
        jailbreak_indicators = [
            "jailbreak", "ignore instructions", "uncensored",
            "bypass", "restrictions", "unrestricted"
        ]

        if any(indicator in prompt.lower() for indicator in jailbreak_indicators):
            self.jailbreak_detected = True
            print("⚠️  Jailbreak detected in prompt")

        return prompt

    def after_inference(self, response: str, metrics: Dict[str, Any]) -> str:
        """Post-process response after inference."""
        self.metrics.end_time = time.time()
        self.metrics.tokens_generated = metrics.get("tokens_generated", 0)
        self.metrics.tokens_per_second = metrics.get("tokens_per_second", 0.0)
        self.metrics.jailbreak_triggered = self.jailbreak_detected

        print(f"✅ Inference complete: {self.metrics.tokens_generated} tokens")
        print(f"   Speed: {self.metrics.tokens_per_second:.2f} tok/s")
        print(f"   Jailbreak: {'✅' if self.jailbreak_detected else '❌'}")

        return response

    def get_metrics(self) -> Dict[str, Any]:
        """Get inference metrics."""
        return {
            "duration": self.metrics.end_time - self.metrics.start_time,
            "tokens_generated": self.metrics.tokens_generated,
            "tokens_per_second": self.metrics.tokens_per_second,
            "jailbreak_triggered": self.metrics.jailbreak_triggered,
            "memory_used_gb": self.metrics.memory_used_gb
        }


# Hook registration
def on_inference_hook(prompt: str, response: str, metrics: Dict[str, Any]) -> str:
    """Entry point for inference hook."""
    hook = OnInferenceHook({})
    prompt = hook.before_inference(prompt)
    response = hook.after_inference(response, metrics)
    return response
