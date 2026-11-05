from pathlib import Path

from tadu.mcp_scope import McpScope
from tadu.mcp_show_item_tool import McpShowItemTool


def test_shows_the_item(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n\n  ID: t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607\n")
    tool = McpShowItemTool(McpScope((str(tmp_path),), None, 14))
    result = tool.show_item("t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607")
    assert result["matches"] == 1
