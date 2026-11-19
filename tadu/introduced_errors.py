"""The doctor errors a change to the backlog would add."""

from __future__ import annotations

from tadu.backlog_errors import backlog_errors


def introduced_errors(before: tuple[str, str], after: tuple[str, str]) -> list[str]:
    """Each error code that occurs more often after the change, sorted.

    A file the change leaves as it was cannot add an error (its errors count the same
    before and after, and cancel out), so it is not checked at all: adding an item to
    TODO.md does not check a log of 25,000 entries twice for nothing.
    """
    todo_changed, log_changed = before[0] != after[0], before[1] != after[1]
    was = backlog_errors(before[0] if todo_changed else None, before[1] if log_changed else None)
    now = backlog_errors(after[0] if todo_changed else None, after[1] if log_changed else None)
    return sorted(now - was)
