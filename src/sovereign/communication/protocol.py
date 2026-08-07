"""SOVEREIGN — protocol definitions (message envelopes)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Envelope:
    """Wire format shared by all transport protocols."""

    version: str = "1.0"
    id: str = ""
    kind: str = "message"       # message | request | response | event | error
    sender: str = ""
    recipient: str = ""
    protocol: str = "sovereign"  # sovereign | mcp | a2a | openai | grpc
    payload: dict[str, Any] = field(default_factory=dict)
    correlation_id: str = ""
    ts: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "id": self.id,
            "kind": self.kind,
            "sender": self.sender,
            "recipient": self.recipient,
            "protocol": self.protocol,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "ts": self.ts,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Envelope":
        return cls(**{k: data.get(k) for k in cls.__dataclass_fields__})
