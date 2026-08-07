"""Unit tests — agents, memory, security."""

from __future__ import annotations

import asyncio

from sovereign.agents.deepseek_chat import DeepSeekChatAgent
from sovereign.memory.memory_manager import MemoryManager
from sovereign.security.authentication import JWTService


def test_agent_lifecycle():
    async def _run() -> None:
        agent = DeepSeekChatAgent(name="test-chat")
        await agent.start()
        result = await agent.run({"input": "hello"})
        status = agent.status()
        assert result["ok"] is True
        assert status["state"] in ("completed", "failed")
        assert status["kind"] == "deepseek.chat"

    asyncio.run(_run())


def test_memory_roundtrip():
    async def _run() -> None:
        mem = MemoryManager()
        await mem.store("working", "k1", {"a": 1})
        assert (await mem.retrieve("working", "k1")) == {"a": 1}
        stats = await mem.get_stats()
        assert stats["working"]["items"] >= 1

    asyncio.run(_run())


def test_jwt_roundtrip():
    jwt = JWTService(secret="unit-test-secret-123")
    token = jwt.issue("alice", {"role": "admin"})
    payload = jwt.verify(token)
    assert payload["sub"] == "alice"
    assert payload["role"] == "admin"
