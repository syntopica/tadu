"""Validate a single-line text value of a task."""

from __future__ import annotations

from tadu.is_one_line import is_one_line


def check_task_text(value: object) -> str | None:
    """A message unless the value is non-empty text on one line."""
    if not isinstance(value, str) or not value.strip() or not is_one_line(value):
        return "must be non-empty text on one line"
    return None
