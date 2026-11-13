from datetime import date

from tadu.card_filter import CardFilter
from tadu.view_entry import ViewEntry
from tadu.view_summary import view_summary


def test_lists_only_the_criteria_that_are_set() -> None:
    view = ViewEntry(
        "hot", CardFilter(project="shop", priority="high", due_before=date(2026, 12, 1))
    )
    assert view_summary(view) == {
        "name": "hot",
        "criteria": "project=shop, priority=high, due_before=2026-12-01",
    }


def test_a_view_without_criteria_has_empty_text() -> None:
    assert view_summary(ViewEntry("all", CardFilter())) == {"name": "all", "criteria": ""}
