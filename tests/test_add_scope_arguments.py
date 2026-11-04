import argparse

import pytest

from tadu.add_scope_arguments import add_scope_arguments


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    add_scope_arguments(root)
    return root


def test_defaults() -> None:
    parsed = parser().parse_args([])
    assert (parsed.paths, parsed.workspace, parsed.done_days) == ([], None, 14)


def test_values() -> None:
    parsed = parser().parse_args(["a", "--workspace", "w", "--done-days", "0"])
    assert (parsed.paths, parsed.workspace, parsed.done_days) == (["a"], "w", 0)


def test_negative_done_days_rejected() -> None:
    with pytest.raises(SystemExit):
        parser().parse_args(["--done-days", "-1"])
