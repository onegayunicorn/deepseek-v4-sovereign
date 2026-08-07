"""SOVEREIGN — DeepSeek-V4 reasoner agent.

Long-form reasoning with ``reasoning_effort`` (low/high/max) and a longer
output budget. Extends the chat agent with reasoner-specific defaults.
"""

from __future__ import annotations

from typing import Any

from sovereign.agents.deepseek_chat import DeepSeekChatAgent

REASONER_SYSTEM_PROMPT = (
    "You are SOVEREIGN's reasoner. Think step by step before answering. "
    "Show your reasoning chain, then a crisp final answer. "
    "Never hide uncertainty."
)


class DeepSeekReasonerAgent(DeepSeekChatAgent):
    kind = "deepseek.reasoner"

    def __init__(self, *, reasoning_effort: str = "high", max_tokens: int = 8192,
                 temperature: float = 0.3, **kwargs: Any):
        super().__init__(
            system_prompt=kwargs.pop("system_prompt", REASONER_SYSTEM_PROMPT),
            max_tokens_hint=max_tokens,
            temperature_hint=temperature,
            **kwargs,
        )
        self.reasoning_effort = reasoning_effort

    async def _act(self, input_: dict[str, Any]) -> dict[str, Any]:
        input_ = {
            **input_,
            "max_tokens": int(input_.get("max_tokens", self.max_tokens_hint)),
            "temperature": float(input_.get("temperature", self.temperature_hint)),
        }
        result = await super()._act(input_)
        if result.get("ok"):
            result["reasoning_effort"] = self.reasoning_effort
        return result
