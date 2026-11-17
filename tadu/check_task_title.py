"""Validate a task title."""

from __future__ import annotations

from tadu.check_task_text import check_task_text

TITLE_LIMIT = 200


def check_task_title(value: object) -> str | None:
    """A message unless the title is one line of at most 200 characters."""
    message = check_task_text(value)
    if message is None and isinstance(value, str) and len(value) > TITLE_LIMIT:
        return f"must be at most {TITLE_LIMIT} characters; move the rest into notes"
    return message
