from pathlib import Path

import pytest

from tadu.card_filter import CardFilter
from tadu.view_filter import view_filter
from tadu.workspace_error import WorkspaceError


def test_no_view_is_empty() -> None:
    assert view_filter(None, None) == CardFilter()


def test_view_needs_workspace() -> None:
    with pytest.raises(WorkspaceError, match=r"^--view needs --workspace$"):
        view_filter(None, "mine")


def test_reads_view_from_workspace(tmp_path: Path) -> None:
    (tmp_path / "tadu-workspace.toml").write_text(
        'version = 1\n\n[[view]]\nname = "ready"\ncolumn = "ready"\n'
    )
    assert view_filter(str(tmp_path), "ready") == CardFilter(column="ready")
