from pathlib import Path

import pytest

from tadu.card_filter import CardFilter
from tadu.find_view import find_view
from tadu.view_entry import ViewEntry
from tadu.workspace import Workspace
from tadu.workspace_error import WorkspaceError


def make(*views: ViewEntry) -> Workspace:
    return Workspace(Path(), (), (), (), (), views)


def test_returns_the_named_filter() -> None:
    wanted = CardFilter(label="bug")
    workspace = make(ViewEntry("a", CardFilter()), ViewEntry("bugs", wanted))
    assert find_view(workspace, "bugs") is wanted


def test_unknown_name_lists_the_known_ones() -> None:
    with pytest.raises(WorkspaceError, match=r"^unknown view x \(views: a\)$"):
        find_view(make(ViewEntry("a", CardFilter())), "x")


def test_no_views_says_none() -> None:
    with pytest.raises(WorkspaceError, match=r"\(views: none\)$"):
        find_view(make(), "x")
