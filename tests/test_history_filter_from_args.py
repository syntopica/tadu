import argparse
from datetime import date

from tadu.history_filter import HistoryFilter
from tadu.history_filter_from_args import history_filter_from_args


def test_fields_repeated_comma_separated_and_aliased() -> None:
    args = argparse.Namespace(
        field=["state, assignee", "label", "", "due"],
        since=date(2026, 11, 1),
        until=None,
        author="",
    )
    assert history_filter_from_args(args) == HistoryFilter(
        frozenset({"state", "assignees", "labels", "due"}), date(2026, 11, 1), None, None
    )


def test_nothing_asked() -> None:
    args = argparse.Namespace(field=[], since=None, until=None, author=None)
    assert history_filter_from_args(args) == HistoryFilter()
