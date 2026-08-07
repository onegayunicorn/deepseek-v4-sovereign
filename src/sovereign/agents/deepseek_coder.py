"""SOVEREIGN — DeepSeek-V4 coder agent.

Code-focused agent: produces structured code changes (files + diffs) that
the tool agent can apply. Temperature biased low for deterministic output.
"""

from __future__ import annotations

from typing import Any

from sovereign.agents.deepseek_chat import DeepSeekChatAgent

CODER_SYSTEM_PROMPT = (
    "You are SOVEREIGN's coding agent. Generate complete, correct, minimal "
    "code. Return JSON with 'summary' and 'changes': [{'path', 'content', "
    "'commit_message'}]. No prose filler."
)


class DeepSeekCoderAgent(DeepSeekChatAgent):
    kind = "deepseek.coder"

    def __init__(self, *, max_tokens: int = 8192, temperature: float = 0.2, **kwargs: Any):
        super().__init__(
            system_prompt=kwargs.pop("system_prompt", CODER_SYSTEM_PROMPT),
            max_tokens_hint=max_tokens,
            temperature_hint=temperature,
            **kwargs,
        )

    async def _act(self, input_: dict[str, Any]) -> dict[str, Any]:
        result = await super()._act({**input_, "max_tokens": 8192, "temperature": 0.2})
        if result.get("ok"):
            import json

            try:
                parsed = json.loads(result["output"])
                if isinstance(parsed, dict) and "changes" in parsed:
                    result["changes"] = parsed["changes"]
                    result["summary"] = parsed.get("summary", "")
            except json.JSONDecodeError:
                pass
        return result
