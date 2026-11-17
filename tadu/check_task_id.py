"""Validate a reference to a task."""

from __future__ import annotations

from tadu.task_id_pattern import TASK_ID_PATTERN


def check_task_id(value: object) -> str | None:
    """A message unless the value is t- followed by a lowercase UUID4."""
    if isinstance(value, str) and TASK_ID_PATTERN.match(value):
        return None
    return "must be a task id: t- and a lowercase UUID4"
