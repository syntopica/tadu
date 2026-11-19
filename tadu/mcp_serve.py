"""Serve MCP over newline-delimited JSON-RPC."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.mcp_handle import mcp_handle

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


def mcp_serve(
    lines: Iterable[str],
    write: Callable[[str], None],
    tools: dict[str, dict[str, object]],
    call: Callable[[str, object], dict[str, object]],
) -> None:
    """Answer each message line until the input ends; a line that is not JSON is a parse error.

    JSON nested too deeply to decode is one too, rather than the end of the server.
    """
    for line in lines:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
        except (ValueError, RecursionError):
            reply: dict[str, object] | None = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }
        else:
            reply = mcp_handle(message, tools, call)
        if reply is not None:
            write(json.dumps(reply, ensure_ascii=False) + "\n")
