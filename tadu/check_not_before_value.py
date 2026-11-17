"""Validate a Not before field value."""

from __future__ import annotations

from tadu.is_iso_date import is_iso_date


def check_not_before_value(value: str) -> str | None:
    """A problem message, or None when the value is a real YYYY-MM-DD date."""
    return None if is_iso_date(value) else "Not before is not a YYYY-MM-DD date"
