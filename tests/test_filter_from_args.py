import argparse
from datetime import date

from tadu.card_filter import CardFilter
from tadu.filter_from_args import filter_from_args


def flags(**given: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "project": None,
        "org": None,
        "role": None,
        "assignee": None,
        "column": None,
        "priority": None,
        "label": None,
        "due_before": None,
        "include_cancelled": False,
    }
    return argparse.Namespace(**(values | given))


def test_copies_flags() -> None:
    args = flags(
        project="p",
        org="o",
        role="r",
        assignee="a",
        column="done",
        priority="low",
        label="l",
        due_before=date(2026, 1, 1),
        include_cancelled=True,
    )
    assert filter_from_args(args, CardFilter()) == CardFilter(
        "p", "o", "r", "a", "done", "low", "l", date(2026, 1, 1), include_cancelled=True
    )


def test_absent_flags_keep_base() -> None:
    base = CardFilter(assignee="ana", column="blocked", include_cancelled=True)
    assert filter_from_args(flags(), base) == base


def test_given_flag_overrides_base() -> None:
    base = CardFilter(assignee="ana", column="blocked")
    assert filter_from_args(flags(column="ready"), base) == CardFilter(
        assignee="ana", column="ready"
    )
