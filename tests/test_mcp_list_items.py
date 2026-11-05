from pathlib import Path

from tadu.card_filter import CardFilter
from tadu.mcp_list_items import mcp_list_items
from tadu.mcp_scope import McpScope


def test_filters_items_and_lists_problems(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n\n  Priority: high\n\n- [ ] B.\n")
    gone = tmp_path / "gone"
    result = mcp_list_items(McpScope((str(tmp_path), str(gone)), None, 14), CardFilter("x"))
    assert result["items"] == []
    result = mcp_list_items(
        McpScope((str(tmp_path), str(gone)), None, 14), CardFilter(priority="high")
    )
    items = result["items"]
    assert isinstance(items, list)
    assert [item["title"] for item in items] == ["A."]
    assert result["problems"] == [
        {"repository": "gone", "message": f"checkout {gone} is not a directory"}
    ]
