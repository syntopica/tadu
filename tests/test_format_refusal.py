import argparse

from tadu.format_refusal import format_refusal
from tadu.operations import OPERATIONS


def args(**given: object) -> argparse.Namespace:
    return argparse.Namespace(**given)


def test_options_of_the_other_format_are_named() -> None:
    add = OPERATIONS["add"]
    given = args(kind="task", check_on="2026-01-01", no_id=True, type=None, note=["n"])
    assert format_refusal(add, given, 2) == "a task backlog takes no --no-id"
    assert format_refusal(add, args(kind="task", check_on="2026-01-01", no_id=False), 1) is None
    tasks = args(type="bug", link=["https://x"], assignees=["ana"], related=[])
    assert format_refusal(add, tasks, 1) == "a TODO.md backlog takes no --type, --link"
    assert format_refusal(add, tasks, 2) is None
    assert format_refusal(OPERATIONS["close"], args(duplicate_of="t-1"), 1) == (
        "a TODO.md backlog takes no --duplicate-of"
    )
