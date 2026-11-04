"""Validate a Priority field value."""

from __future__ import annotations

from tadu.priorities import PRIORITIES


def check_priority_value(value: str) -> str | None:
    """A problem message, or None when the value is a known priority."""
    if value in PRIORITIES:
        return None
    return "Priority is not one of urgent, high, normal, low"
