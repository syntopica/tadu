from pathlib import Path

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from tadu.mcp_load_cards import mcp_load_cards
from tadu.mcp_scope import McpScope


def test_reads_paths_and_reports_problems(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n")
    cards, problems = mcp_load_cards(McpScope((str(tmp_path), str(tmp_path / "gone")), None, 14))
    assert [card.item.title for card in cards] == ["A."]
    assert [problem.repository for problem in problems] == ["gone"]


def test_bad_workspace_is_a_tool_error(tmp_path: Path) -> None:
    with pytest.raises(ToolError, match=r"tadu-workspace\.toml"):
        mcp_load_cards(McpScope((), str(tmp_path), 14))
