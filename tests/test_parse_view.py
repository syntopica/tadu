from datetime import date

import pytest

from tadu.card_filter import CardFilter
from tadu.parse_view import parse_view
from tadu.view_entry import ViewEntry
from tadu.workspace_error import WorkspaceError


def test_reads_every_criterion() -> None:
    row: dict[str, object] = {
        "name": "urgent",
        "project": "p",
        "org": "acme",
        "role": "client",
        "assignee": "ana",
        "column": "blocked",
        "priority": "urgent",
        "kind": "later",
        "label": "bug",
        "due_before": date(2026, 12, 31),
        "include_cancelled": True,
        "open": True,
    }
    assert parse_view(row) == ViewEntry(
        "urgent",
        CardFilter(
            "p",
            "acme",
            "client",
            "ana",
            "blocked",
            "urgent",
            "later",
            "bug",
            date(2026, 12, 31),
            include_cancelled=True,
            open=True,
        ),
    )


def test_name_only_is_an_empty_filter() -> None:
    assert parse_view({"name": "all"}) == ViewEntry("all", CardFilter())


@pytest.mark.parametrize(
    ("row", "fragment"),
    [
        ({}, "view: name must be a string"),
        ({"name": "x", "colour": "red"}, "view: unknown key colour"),
        ({"name": "x", "priority": "soon"}, "view: priority must be one of"),
        ({"name": "x", "kind": "someday"}, "view: kind must be one of"),
    ],
)
def test_bad_rows_are_errors(row: dict[str, object], fragment: str) -> None:
    with pytest.raises(WorkspaceError, match=fragment):
        parse_view(row)
