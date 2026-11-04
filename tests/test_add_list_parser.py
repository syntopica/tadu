import argparse
from datetime import date

import pytest

from tadu.add_list_parser import add_list_parser


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    add_list_parser(root.add_subparsers(dest="command"))
    return root


def test_filters() -> None:
    parsed = parser().parse_args(
        ["list", "--priority", "high", "--column", "done", "--due-before", "2026-12-01", "--json"]
    )
    assert (parsed.priority, parsed.column, parsed.due_before, parsed.json) == (
        "high",
        "done",
        date(2026, 12, 1),
        True,
    )
    assert parsed.include_cancelled is False


@pytest.mark.parametrize("flag", [["--priority", "x"], ["--column", "x"]])
def test_bad_choices_rejected(flag: list[str]) -> None:
    with pytest.raises(SystemExit):
        parser().parse_args(["list", *flag])
