import argparse
from datetime import date

from tadu.card_filter import CardFilter
from tadu.filter_from_args import filter_from_args


def test_copies_flags() -> None:
    args = argparse.Namespace(
        project="p",
        org="o",
        role="r",
        assignee="a",
        column="done",
        priority="low",
        kind="waiting",
        label="l",
        due_before=date(2026, 1, 1),
        check_before=date(2026, 2, 1),
        include_cancelled=True,
        open=True,
    )
    assert filter_from_args(args) == CardFilter(
        "p",
        "o",
        "r",
        "a",
        "done",
        "low",
        "waiting",
        "l",
        date(2026, 1, 1),
        date(2026, 2, 1),
        include_cancelled=True,
        open=True,
    )
