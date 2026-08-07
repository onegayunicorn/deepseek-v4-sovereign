"""SOVEREIGN — Agent-to-Agent (A2A) protocol adapter.

Implements the A2A agent-card handshake and message envelope mapping onto
the sovereign :class:`Envelope`. Transport-agnostic: plug any HTTP/WS
carrier behind ``send``.
"""

from __future__ import annotations

from typing import Any

from sovereign.communication.protocol import Envelope
from sovereign.utils.id_generator import uuid4

PROTOCOL_VERSION = "0.2.0"


def agent_card(agent_id: str, name: str, description: str, skills: list[str]) -> dict[str, Any]:
    """A2A AgentCard representation of a sovereign agent."""
    return {
        "name": name,
        "description": description,
        "url": f"agent://{agent_id}",
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {"skills": skills, "streaming": False},
        "skills": [{"id": s, "name": s} for s in skills],
    }


def to_a2a_message(envelope: Envelope) -> dict[str, Any]:
    """Map a sovereign envelope onto an A2A message."""
    return {
        "messageId": envelope.id or uuid4(),
        "kind": envelope.kind,
        "sender": {"agentId": envelope.sender},
        "recipient": {"agentId": envelope.recipient},
        "payload": {"type": "text", "text": envelope.payload.get("text", "")},
        "correlationId": envelope.correlation_id or None,
    }


def from_a2a_message(message: dict[str, Any]) -> Envelope:
    """Parse an A2A message into a sovereign envelope."""
    sender = message.get("sender", {}).get("agentId", "")
    recipient = message.get("recipient", {}).get("agentId", "")
    payload = message.get("payload", {})
    return Envelope(
        id=message.get("messageId", ""),
        kind=message.get("kind", "message"),
        sender=sender,
        recipient=recipient,
        protocol="a2a",
        payload={"text": payload.get("text", "")},
        correlation_id=message.get("correlationId", ""),
    )
