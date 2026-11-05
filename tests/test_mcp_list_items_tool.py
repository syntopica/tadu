from pathlib import Path

from tadu.mcp_list_items_tool import McpListItemsTool
from tadu.mcp_scope import McpScope
from tadu.mcp_where import McpWhere


def test_applies_where(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n\n  Priority: high\n\n- [ ] B.\n")
    tool = McpListItemsTool(McpScope((str(tmp_path),), None, 14))
    everything = tool.list_items()["items"]
    assert isinstance(everything, list)
    assert len(everything) == 2
    high = tool.list_items(McpWhere(priority="high"))["items"]
    assert isinstance(high, list)
    assert [item["title"] for item in high] == ["A."]
