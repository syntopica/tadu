"""Tell a real calendar date written YYYY-MM-DD."""

from __future__ import annotations

from datetime import date


def is_real_date(value: object) -> bool:
    """True for a string that is exactly the ISO form of a calendar date."""
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False
