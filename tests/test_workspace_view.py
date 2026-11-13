from pathlib import Path

import pytest

from tadu.card_filter import CardFilter
from tadu.workspace_error import WorkspaceError
from tadu.workspace_view import workspace_view


def test_reads_the_view_from_the_workspace_file(tmp_path: Path) -> None:
    (tmp_path / "tadu-workspace.toml").write_text(
        'version = 1\n[[view]]\nname = "bugs"\nlabel = "bug"\n'
    )
    assert workspace_view(str(tmp_path), "bugs") == CardFilter(label="bug")


def test_needs_a_workspace() -> None:
    with pytest.raises(WorkspaceError, match=r"^--view needs --workspace$"):
        workspace_view(None, "bugs")
