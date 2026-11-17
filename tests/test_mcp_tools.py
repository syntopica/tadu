from tadu.mcp_property import mcp_property
from tadu.mcp_tool import mcp_tool
from tadu.mcp_tools import MCP_TOOLS
from tadu.mcp_versions import MCP_VERSIONS


def test_property_shapes() -> None:
    assert mcp_property("array", "d") == {
        "type": "array",
        "description": "d",
        "items": {"type": "string"},
    }
    assert mcp_property("integer", "d") == {"type": "integer", "description": "d", "minimum": 0}
    assert mcp_property("string", "d", ("a",)) == {
        "type": "string",
        "description": "d",
        "enum": ["a"],
    }


def test_tool_shape_and_hints() -> None:
    tool = mcp_tool("t", "d", {}, ("x",), read_only=False)
    assert tool["inputSchema"] == {
        "type": "object",
        "properties": {},
        "required": ["x"],
        "additionalProperties": False,
    }
    assert tool["annotations"] == {
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }


def test_served_tools() -> None:
    assert list(MCP_TOOLS) == ["next", "inbox", "urgent", "list", "show", "add", "mark", "close"]
    writes = [name for name, tool in MCP_TOOLS.items() if not tool["annotations"]["readOnlyHint"]]  # type: ignore[index]
    assert writes == ["add", "mark", "close"]
    for tool in MCP_TOOLS.values():
        schema = tool["inputSchema"]
        assert isinstance(schema, dict)
        assert set(schema["required"]) <= set(schema["properties"])
    assert MCP_VERSIONS[0] == "2025-11-25"
