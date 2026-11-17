"""Answer one JSON-RPC message of the MCP protocol."""

from __future__ import annotations

from importlib.metadata import version
from typing import TYPE_CHECKING

from tadu.mcp_instructions import MCP_INSTRUCTIONS
from tadu.mcp_tools import MCP_TOOLS
from tadu.mcp_versions import MCP_VERSIONS

if TYPE_CHECKING:
    from collections.abc import Callable


def mcp_handle(
    message: object, call: Callable[[str, object], dict[str, object]]
) -> dict[str, object] | None:
    """The response, or None for a notification; `call` runs a tool that exists."""
    if not isinstance(message, dict) or not isinstance(message.get("method"), str):
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32600, "message": "Invalid Request"},
        }
    if "id" not in message:
        return None
    method, params = message["method"], message.get("params") or {}
    reply: dict[str, object] = {"jsonrpc": "2.0", "id": message["id"]}
    if method == "initialize":
        asked = params.get("protocolVersion") if isinstance(params, dict) else None
        reply["result"] = {
            "protocolVersion": asked if asked in MCP_VERSIONS else MCP_VERSIONS[0],
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "tadu", "version": version("tadu")},
            "instructions": MCP_INSTRUCTIONS,
        }
    elif method == "ping":
        reply["result"] = {}
    elif method == "tools/list":
        reply["result"] = {"tools": list(MCP_TOOLS.values())}
    elif method == "tools/call" and isinstance(params, dict) and params.get("name") in MCP_TOOLS:
        reply["result"] = call(str(params["name"]), params.get("arguments", {}))
    elif method == "tools/call":
        reply["error"] = {"code": -32602, "message": "Unknown tool"}
    else:
        reply["error"] = {"code": -32601, "message": f"Method not found: {method}"}
    return reply
