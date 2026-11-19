from tadu.operation import Operation
from tadu.operation_tool import operation_tool
from tadu.operations import OPERATIONS
from tadu.param import Param
from tadu.param_property import param_property


def test_property_shapes() -> None:
    assert param_property(Param("a", "list", "d")) == {
        "type": "array",
        "description": "d",
        "items": {"type": "string"},
    }
    assert param_property(Param("n", "count", "d")) == {
        "type": "integer",
        "description": "d",
        "minimum": 0,
    }
    assert param_property(Param("c", "choice", "d", ("a",))) == {
        "type": "string",
        "description": "d",
        "enum": ["a"],
    }
    assert param_property(Param("f", "flag", "d")) == {"type": "boolean", "description": "d"}
    assert param_property(Param("s", "day", "from then")) == {
        "type": "string",
        "description": "YYYY-MM-DD; from then",
    }


def test_a_change_takes_repository_and_preview() -> None:
    operation = Operation("t", "help", (Param("x", "text", "x", required=True),), access="write")
    tool = operation_tool(operation)
    assert tool["description"] == "help"
    assert tool["inputSchema"]["required"] == ["x"]  # type: ignore[index]
    assert list(tool["inputSchema"]["properties"]) == ["x", "repository", "preview"]  # type: ignore[index]
    assert tool["inputSchema"]["additionalProperties"] is False  # type: ignore[index]
    assert tool["annotations"] == {
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }


def test_hints_follow_the_access() -> None:
    show, migrate = operation_tool(OPERATIONS["show"]), operation_tool(OPERATIONS["migrate"])
    assert show["annotations"]["readOnlyHint"] is True  # type: ignore[index]
    assert show["annotations"]["idempotentHint"] is True  # type: ignore[index]
    assert migrate["annotations"]["destructiveHint"] is True  # type: ignore[index]
    assert "preview" not in show["inputSchema"]["properties"]  # type: ignore[index]
    assert show["description"] == OPERATIONS["show"].describe


def test_a_member_of_a_group_is_not_required_alone() -> None:
    close = operation_tool(OPERATIONS["close"])["inputSchema"]
    assert close["required"] == []  # type: ignore[index]
    assert {"id", "match", "evidence", "resolution"} <= set(close["properties"])  # type: ignore[index]
