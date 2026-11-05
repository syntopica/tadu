from pathlib import Path

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from tadu.mcp_scope import McpScope
from tadu.mcp_show_item import mcp_show_item

ITEM = "- [ ] A.\n\n  ID: t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607\n"
KEY = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"


def repo(root: Path) -> str:
    root.mkdir()
    (root / "TODO.md").write_text(ITEM)
    return str(root)


def test_first_match_and_count(tmp_path: Path) -> None:
    scope = McpScope((repo(tmp_path / "one"), repo(tmp_path / "two")), None, 14)
    result = mcp_show_item(scope, KEY)
    assert result["matches"] == 2
    item = result["item"]
    assert isinstance(item, dict)
    assert item["repository"] == "one"


def test_unknown_key(tmp_path: Path) -> None:
    with pytest.raises(ToolError, match="no item nope"):
        mcp_show_item(McpScope((repo(tmp_path / "one"),), None, 14), "nope")
