"""`tadu mcp` as the official MCP SDK's client sees it.

tadu serves MCP by hand (no dependency, ~4x faster to start than on the SDK); the SDK's
client is the referee that it speaks the protocol.
"""

import asyncio
import sys
from pathlib import Path

from board_workspace import board_workspace
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.exceptions import MCPError
from mcp.types import CallToolResult, TextContent


def text_of(result: CallToolResult) -> str:
    first = result.content[0]
    assert isinstance(first, TextContent)
    return first.text


async def session_with_tadu(repository: Path) -> dict[str, object]:
    code = "import sys; from tadu.cli import main; sys.exit(main(sys.argv[1:]))"
    params = StdioServerParameters(
        command=sys.executable, args=["-c", code, "mcp", str(repository)]
    )
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        init = await session.initialize()
        tools = await session.list_tools()
        listed = await session.call_tool("list", {})
        wrong = await session.call_tool("list", {"no_such_argument": 1})
        unknown: object = None
        try:
            await session.call_tool("no_such_tool", {})
        except MCPError as error:  # the spec: an unknown tool is a protocol error
            unknown = (error.code, error.message)
        return {
            "server": init.server_info.name,
            "protocol": init.protocol_version,
            "instructions": bool(init.instructions),
            "tools": [tool.name for tool in tools.tools],
            "read_only": {
                tool.name: tool.annotations.read_only_hint
                for tool in tools.tools
                if tool.annotations
            },
            "listed": (listed.is_error, text_of(listed)),
            "wrong": (wrong.is_error, text_of(wrong)),
            "unknown": unknown,
        }


def test_the_sdk_client_speaks_with_tadu(tmp_path: Path) -> None:
    board_workspace(tmp_path)
    seen = asyncio.run(session_with_tadu(tmp_path / "shop"))
    assert seen["server"] == "tadu"
    assert seen["protocol"] == "2025-11-25"
    assert seen["instructions"] is True
    assert seen["tools"] == ["next", "inbox", "urgent", "list", "show", "add", "mark", "close"]
    assert seen["read_only"] == {
        "next": True,
        "inbox": True,
        "urgent": True,
        "list": True,
        "show": True,
        "add": False,
        "mark": False,
        "close": False,
    }
    listed = seen["listed"]
    assert isinstance(listed, tuple)
    assert listed[0] is False
    assert "<script>alert(1)</script>" in listed[1]
    assert seen["wrong"] == (True, "unknown arguments: no_such_argument")
    assert seen["unknown"] == (-32602, "Unknown tool")
