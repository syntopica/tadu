import json
from pathlib import Path

import anyio
import pytest
from mcp import Client
from mcp.types import CallToolResult, ListToolsResult

from tadu.build_mcp_server import build_mcp_server
from tadu.mcp_scope import McpScope

ITEMS = "- [ ] A.\n\n  Priority: high\n\n- [!] B.\n"


def scope(tmp_path: Path) -> McpScope:
    (tmp_path / "TODO.md").write_text(ITEMS)
    return McpScope((str(tmp_path),), None, 14)


def list_tools(server_scope: McpScope) -> ListToolsResult:
    async def run() -> ListToolsResult:
        async with Client(build_mcp_server(server_scope)) as client:
            return await client.list_tools()

    return anyio.run(run)


def call(server_scope: McpScope, name: str, arguments: dict[str, object]) -> CallToolResult:
    async def run() -> CallToolResult:
        async with Client(build_mcp_server(server_scope)) as client:
            return await client.call_tool(name, arguments)

    return anyio.run(run)


def test_tools_are_read_only(tmp_path: Path) -> None:
    tools = list_tools(scope(tmp_path)).tools
    assert [tool.name for tool in tools] == ["list_items", "show_item"]
    for tool in tools:
        assert tool.annotations is not None
        assert tool.annotations.read_only_hint is True
        assert tool.annotations.open_world_hint is False
    assert "in_progress" in str(tools[0].description)


def test_list_items_filters(tmp_path: Path) -> None:
    result = call(scope(tmp_path), "list_items", {"where": {"column": "blocked"}})
    assert result.is_error is False
    assert result.structured_content is not None
    assert [item["title"] for item in result.structured_content["items"]] == ["B."]


def test_list_items_without_filter(tmp_path: Path) -> None:
    result = call(scope(tmp_path), "list_items", {})
    assert result.structured_content is not None
    assert len(result.structured_content["items"]) == 2


def test_show_item(tmp_path: Path) -> None:
    server_scope = scope(tmp_path)
    listed = call(server_scope, "list_items", {"where": {"priority": "high"}})
    assert listed.structured_content is not None
    key = listed.structured_content["items"][0]["key"]
    shown = call(server_scope, "show_item", {"key": key})
    assert shown.structured_content is not None
    assert shown.structured_content["item"]["text"] == "- [ ] A.\n\n  Priority: high"
    assert shown.structured_content["matches"] == 1


def test_errors_are_tool_errors(tmp_path: Path) -> None:
    unknown = call(scope(tmp_path), "show_item", {"key": "nope"})
    assert unknown.is_error is True
    assert "no item nope" in json.dumps(unknown.model_dump(mode="json"))
    bad_date = call(scope(tmp_path), "list_items", {"where": {"due_before": "soon"}})
    assert bad_date.is_error is True


@pytest.mark.parametrize(
    "where",
    [{"colum": "blocked"}, {"column": "doing"}, {"priority": "critical"}],
)
def test_malformed_filters_are_tool_errors(tmp_path: Path, where: dict[str, object]) -> None:
    result = call(scope(tmp_path), "list_items", {"where": where})
    assert result.is_error is True
    assert result.structured_content is None


def test_schema_lists_the_choices(tmp_path: Path) -> None:
    schema = json.dumps(list_tools(scope(tmp_path)).tools[0].input_schema)
    assert '"additionalProperties": false' in schema
    assert '"in_progress"' in schema
    assert '"urgent"' in schema
