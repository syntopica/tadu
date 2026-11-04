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
        label="l",
        due_before=date(2026, 1, 1),
        include_cancelled=True,
    )
    assert filter_from_args(args) == CardFilter(
        "p", "o", "r", "a", "done", "low", "l", date(2026, 1, 1), include_cancelled=True
    )
