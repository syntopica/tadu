"""Validate a task estimate."""

from __future__ import annotations

ESTIMATE_LIMIT = 999_999_999


def check_task_estimate(value: object) -> str | None:
    """A message unless the value is a whole number of minutes from 1 to 999999999."""
    if isinstance(value, bool) or not isinstance(value, int) or not 0 < value <= ESTIMATE_LIMIT:
        return "must be a whole number of minutes from 1 to 999999999"
    return None
