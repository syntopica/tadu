from datetime import date

from tadu.card_filter import CardFilter
from tadu.mcp_card_filter import mcp_card_filter
from tadu.mcp_where import McpWhere


def test_absent_where_is_an_empty_filter() -> None:
    assert mcp_card_filter(None) == CardFilter()


def test_copies_every_criterion() -> None:
    where = McpWhere(
        project="p",
        org="o",
        role="r",
        assignee="a",
        column="ready",
        priority="low",
        label="l",
        due_before=date(2026, 11, 5),
        include_cancelled=True,
    )
    assert mcp_card_filter(where) == CardFilter(
        "p", "o", "r", "a", "ready", "low", "l", date(2026, 11, 5), include_cancelled=True
    )
