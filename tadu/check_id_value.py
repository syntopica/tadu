"""Validate an ID field value."""

from __future__ import annotations

from tadu.task_id_pattern import TASK_ID_PATTERN


def check_id_value(value: str) -> str | None:
    """A problem message, or None when the value is t- followed by a UUID4."""
    if TASK_ID_PATTERN.match(value):
        return None
    return "ID is not t- followed by a UUID4"
