"""Validate a date value of a task."""

from __future__ import annotations

from tadu.is_real_date import is_real_date


def check_task_date(value: object) -> str | None:
    """A message unless the value is a real YYYY-MM-DD date."""
    return None if is_real_date(value) else "must be a YYYY-MM-DD date"
