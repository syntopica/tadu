import json

from tadu.mcp_handle import mcp_handle
from tadu.mcp_instructions import MCP_INSTRUCTIONS
from tadu.mcp_serve import mcp_serve
from tadu.operation_tools import operation_tools

TOOLS = operation_tools("read")


def call(name: str, arguments: object) -> dict[str, object]:
    return {"content": [{"type": "text", "text": f"{name} {arguments}"}], "isError": False}


def handle(method: str, params: object = None, **extra: object) -> dict[str, object] | None:
    return mcp_handle(
        {"jsonrpc": "2.0", "id": 7, "method": method, "params": params, **extra}, TOOLS, call
    )


def test_initialize_negotiates_and_instructs() -> None:
    reply = handle("initialize", {"protocolVersion": "2025-03-26"})
    assert reply is not None
    result = reply["result"]
    assert isinstance(result, dict)
    assert result["protocolVersion"] == "2025-03-26"
    assert result["capabilities"] == {"tools": {"listChanged": False}}
    assert result["serverInfo"]["name"] == "tadu"
    assert result["instructions"] == MCP_INSTRUCTIONS
    newer = handle("initialize", {"protocolVersion": "2099-01-01"})
    assert newer is not None
    assert newer["result"]["protocolVersion"] == "2025-11-25"  # type: ignore[index]
    assert handle("initialize") is not None


def test_tools_ping_and_errors() -> None:
    listed = handle("tools/list")
    assert listed is not None
    assert len(listed["result"]["tools"]) == 10  # type: ignore[index]
    assert handle("ping") == {"jsonrpc": "2.0", "id": 7, "result": {}}
    called = handle("tools/call", {"name": "next", "arguments": {"json": True}})
    assert called is not None
    assert called["result"]["content"][0]["text"] == "next {'json': True}"  # type: ignore[index]
    assert handle("tools/call", {"name": "add"}) == {
        "jsonrpc": "2.0",
        "id": 7,
        "error": {"code": -32602, "message": "Unknown tool"},
    }
    assert handle("server/discover") == {
        "jsonrpc": "2.0",
        "id": 7,
        "error": {"code": -32601, "message": "Method not found: server/discover"},
    }


def test_notifications_get_no_reply_and_junk_is_refused() -> None:
    assert (
        mcp_handle({"jsonrpc": "2.0", "method": "notifications/initialized"}, TOOLS, call) is None
    )
    invalid = {"code": -32600, "message": "Invalid Request"}
    assert mcp_handle([1], TOOLS, call) == {"jsonrpc": "2.0", "id": None, "error": invalid}


def test_serve_answers_each_line() -> None:
    written: list[str] = []
    lines = ['{"jsonrpc":"2.0","id":1,"method":"ping"}\n', "\n", "not json\n", '{"method":"x"}\n']
    mcp_serve(lines, written.append, TOOLS, call)
    replies = [json.loads(line) for line in written]
    assert replies == [
        {"jsonrpc": "2.0", "id": 1, "result": {}},
        {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
    ]
