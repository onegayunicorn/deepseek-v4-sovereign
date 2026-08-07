"""SOVEREIGN — gRPC service definitions (protobuf mapping).

Provides the protobuf service/message skeleton for the gRPC transport and
a codec between sovereign envelopes and gRPC byte payloads. The actual
``grpcio`` server can be generated from ``proto/sovereign.proto``.
"""

from __future__ import annotations

import json
from typing import Any

from sovereign.communication.protocol import Envelope

SERVICE_DEFINITION = """
syntax = "proto3";
package sovereign.v1;

service Orchestrator {
  rpc SubmitTask(TaskRequest) returns (TaskReply);
  rpc StreamEvents(EventFilter) returns (stream Event);
  rpc InvokeTool(ToolRequest) returns (ToolReply);
  rpc Ping(Empty) returns (Empty);
}

message Empty {}
message TaskRequest { string type = 1; string payload_json = 2; int32 priority = 3; }
message TaskReply { string task_id = 1; string status = 2; }
message ToolRequest { string name = 1; string arguments_json = 2; }
message ToolReply { string result_json = 1; bool ok = 2; }
message EventFilter { string event_type = 1; }
message Event { string id = 1; string type = 2; string payload_json = 3; }
"""


def envelope_to_bytes(envelope: Envelope) -> bytes:
    """Serialize an envelope as JSON bytes for gRPC transport."""
    return json.dumps(envelope.to_dict()).encode()


def bytes_to_envelope(data: bytes) -> Envelope:
    return Envelope.from_dict(json.loads(data.decode()))
