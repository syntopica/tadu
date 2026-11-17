"""Read an optional day from text."""

from __future__ import annotations

from datetime import date


def text_day(text: str | None) -> date | None:
    """The date of a YYYY-MM-DD text, or None."""
    return date.fromisoformat(text) if text else None
