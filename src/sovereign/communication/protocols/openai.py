"""SOVEREIGN — OpenAI-compatible chat protocol adapter.

Lets any OpenAI-compatible client (including DeepSeek-V4-Flash-0731 via the
HuggingFace router) talk to sovereign agents through the standard
``/chat/completions`` contract.
"""

from __future__ import annotations

from typing import Any, AsyncIterator

from sovereign.agents.base import BaseAgent


async def chat_completion(agent: BaseAgent, messages: list[dict[str, Any]],
                          *, model: str = "deepseek-v4-sovereign", stream: bool = False,
                          temperature: float = 1.0, max_tokens: int = 8192) -> dict[str, Any]:
    """Serve one chat completion request through a sovereign agent."""
    content = "\n".join(
        f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages
    )
    result = await agent.run({"input": content, "max_tokens": max_tokens, "temperature": temperature})
    text = str(result.get("output", result))

    if stream:
        return {
            "object": "chat.completion.chunk",
            "model": model,
            "choices": [{"index": 0, "delta": {"content": text}, "finish_reason": "stop"}],
        }
    return {
        "id": f"chatcmpl-{agent.agent_id}",
        "object": "chat.completion",
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": len(content), "completion_tokens": len(text), "total_tokens": len(content) + len(text)},
    }
