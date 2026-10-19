import argparse
from datetime import date

import pytest

from tadu.add_close_parser import add_close_parser


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="tadu")
    add_close_parser(root.add_subparsers(dest="command"))
    return root


def test_defaults_and_date() -> None:
    parsed = parser().parse_args(
        ["close", "--match", "a", "--evidence", "e", "--date", "2026-10-19"]
    )
    assert (parsed.path, parsed.date, parsed.write) == (".", date(2026, 10, 19), False)


def test_evidence_and_resolution_exclude_each_other() -> None:
    with pytest.raises(SystemExit):
        parser().parse_args(["close", "--match", "a", "--evidence", "e", "--resolution", "r"])
