"""The doctor errors a change to the backlog would add."""

from __future__ import annotations

from tadu.backlog_errors import backlog_errors


def introduced_errors(before: tuple[str, str], after: tuple[str, str]) -> list[str]:
    """Each error code that occurs more often after the change, sorted."""
    added = backlog_errors(*after) - backlog_errors(*before)
    return sorted(added)
