from pathlib import Path

import pytest

from tadu.card_filter import CardFilter
from tadu.find_view import find_view
from tadu.view_entry import ViewEntry
from tadu.workspace import Workspace
from tadu.workspace_error import WorkspaceError


def make(*views: ViewEntry) -> Workspace:
    return Workspace(Path(), (), (), (), (), views)


def test_found() -> None:
    wanted = CardFilter(column="ready")
    workspace = make(ViewEntry("a", CardFilter()), ViewEntry("ready", wanted))
    assert find_view(workspace, "ready") == wanted


def test_unknown_lists_known() -> None:
    with pytest.raises(WorkspaceError, match=r"^unknown view x \(known: a, b\)$"):
        find_view(make(ViewEntry("a", CardFilter()), ViewEntry("b", CardFilter())), "x")


def test_unknown_without_views() -> None:
    with pytest.raises(WorkspaceError, match=r"\(known: none\)$"):
        find_view(make(), "x")
