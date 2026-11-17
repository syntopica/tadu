"""Validate a slug value of a task."""

from __future__ import annotations

from tadu.label_pattern import LABEL_PATTERN


def check_task_slug(value: object) -> str | None:
    """A message unless the value is lowercase letters, digits and hyphens."""
    if isinstance(value, str) and LABEL_PATTERN.match(value):
        return None
    return "must be a slug: lowercase letters, digits and hyphens"
