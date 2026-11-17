"""Validate a Check on field value."""

from __future__ import annotations

from tadu.is_iso_date import is_iso_date


def check_check_on_value(value: str) -> str | None:
    """A problem message, or None when the value is a real YYYY-MM-DD date."""
    return None if is_iso_date(value) else "Check on is not a YYYY-MM-DD date"
