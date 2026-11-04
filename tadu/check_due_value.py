"""Validate a Due field value."""

from __future__ import annotations

from datetime import date


def check_due_value(value: str) -> str | None:
    """A problem message, or None when the value is a real YYYY-MM-DD date."""
    try:
        if date.fromisoformat(value).isoformat() == value:
            return None
    except ValueError:
        pass
    return "Due is not a YYYY-MM-DD date"
