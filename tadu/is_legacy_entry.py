"""Decide whether a log entry predates the marker date."""

from __future__ import annotations

from datetime import date


def is_legacy_entry(stamp: str, since: date) -> bool:
    """True when the entry date parses and is before `since`."""
    try:
        return date.fromisoformat(stamp) < since
    except ValueError:
        return False
