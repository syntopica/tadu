from datetime import date

import pytest

from tadu.card_filter import CardFilter
from tadu.parse_view import parse_view
from tadu.view_entry import ViewEntry
from tadu.workspace_error import WorkspaceError


def test_every_criterion() -> None:
    row: dict[str, object] = {
        "name": "mine",
        "project": "p",
        "org": "o",
        "role": "r",
        "assignee": "ana",
        "column": "blocked",
        "priority": "high",
        "label": "l",
        "due_before": date(2026, 12, 1),
        "include_cancelled": True,
    }
    assert parse_view(row) == ViewEntry(
        "mine",
        CardFilter(
            "p", "o", "r", "ana", "blocked", "high", "l", date(2026, 12, 1), include_cancelled=True
        ),
    )


def test_name_only_is_empty_filter() -> None:
    assert parse_view({"name": "all"}) == ViewEntry("all", CardFilter())


def test_name_required() -> None:
    with pytest.raises(WorkspaceError, match=r"^view: name must be a string$"):
        parse_view({"column": "ready"})


def test_unknown_key() -> None:
    with pytest.raises(WorkspaceError, match=r"^view: unknown key colour$"):
        parse_view({"name": "x", "colour": "red"})


def test_bad_column() -> None:
    with pytest.raises(WorkspaceError, match=r"^view: column must be one of "):
        parse_view({"name": "x", "column": "doing"})
