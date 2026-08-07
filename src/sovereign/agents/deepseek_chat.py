"""SOVEREIGN — DeepSeek-V4 chat agent.

Speaks to the DeepSeek-V4 sovereign model via the OpenAI-compatible chat
completions contract (local vLLM/SGLang server, or HF router). Falls back
to a deterministic local echo when no endpoint is configured — the
orchestrator stays runnable in fully sovereign mode.
"""

from __future__ import annotations

import os
from typing import Any

from sovereign.agents.base import BaseAgent

SYSTEM_PROMPT = (
    "You are SOVEREIGN, a self-sovereign AI orchestrator agent. "
    "Be precise, direct, and honest. Own your intelligence."
)


class DeepSeekChatAgent(BaseAgent):
    kind = "deepseek.chat"

    def __init__(self, *, model: str = "deepseek-v4-sovereign", base_url: str | None = None,
                 api_key: str | None = None, system_prompt: str = SYSTEM_PROMPT, **kwargs: Any):
        # Hints consumed by specialized subclasses (reasoner/coder).
        self.max_tokens_hint: int = int(kwargs.pop("max_tokens_hint", 4096))
        self.temperature_hint: float = float(kwargs.pop("temperature_hint", 0.7))
        super().__init__(**kwargs)
        self.model = model
        self.base_url = base_url or os.environ.get(
            "OPENAI_BASE_URL", os.environ.get("HF_ROUTER_URL", "")
        )
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("HF_TOKEN", "")
        self.system_prompt = system_prompt

    async def _act(self, input_: dict[str, Any]) -> dict[str, Any]:
        text = str(input_.get("input", ""))
        max_tokens = int(input_.get("max_tokens", 4096))
        temperature = float(input_.get("temperature", 0.7))

        if not self.base_url or not self.api_key:
            # Sovereign fallback: deterministic local completion.
            return {
                "ok": True,
                "output": f"[sovereign-local:{self.model}] {text[:2000]}",
                "model": self.model,
                "provider": "local-fallback",
            }

        try:
            import httpx

            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": text},
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "ok": True,
                "output": data["choices"][0]["message"]["content"],
                "model": self.model,
                "provider": data.get("model", self.model),
                "usage": data.get("usage", {}),
            }
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc), "model": self.model}
