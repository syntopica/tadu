"""Whether a text is a real calendar date written YYYY-MM-DD."""

from __future__ import annotations

from datetime import date


def is_iso_date(value: str) -> bool:
    """True for a date that exists, written exactly as `date.isoformat` writes it."""
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False
