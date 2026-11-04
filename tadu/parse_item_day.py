"""The day written before an item's title."""

from __future__ import annotations

from datetime import date


def parse_item_day(text: str | None) -> date | None:
    """The date, or None when absent or not a real calendar day."""
    if text is None:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None
