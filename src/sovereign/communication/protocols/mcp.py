"""SOVEREIGN — Model Context Protocol (MCP) adapter.

Exposes the orchestrator's tools/agents as an MCP server over stdio or SSE.
Minimal JSON-RPC framing per the MCP spec; a full SDK (``mcp``) can replace
the transport without changing the tool surface.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from sovereign.tools.registry import ToolRegistry


def _rpc(method: str, params: dict[str, Any], msg_id: int | None = None) -> dict[str, Any]:
    message: dict[str, Any] = {"jsonrpc": "2.0", "method": method, "params": params}
    if msg_id is not None:
        message["id"] = msg_id
    return message


class MCPStdioServer:
    """Serve tools over MCP stdio transport (one request per line)."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def _handle(self, request: dict[str, Any]) -> dict[str, Any]:
        method = request.get("method")
        params = request.get("params", {}) or {}
        msg_id = request.get("id")
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "sovereign", "version": "1.0.0"},
            }}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {
                "tools": [{"name": s["name"], "description": s["description"]}
                          for s in self.registry.specs()]}}
        if method == "tools/call":
            tool_name = params.get("name", "")
            spec = self.registry.get(tool_name)
            if spec is None:
                return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32602, "message": f"unknown tool: {tool_name}"}}
            result = spec.fn(**params.get("arguments", {}))
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": json.dumps(result)}]}}
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"method not found: {method}"}}

    def serve_forever(self) -> None:
        """Read JSON-RPC requests from stdin; write responses to stdout."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                response = self._handle(request)
            except json.JSONDecodeError:
                response = {"jsonrpc": "2.0", "error": {"code": -32700, "message": "parse error"}}
            print(json.dumps(response), flush=True)
