"""Today's date where tadu runs."""

from __future__ import annotations

from datetime import UTC, date, datetime


def local_today() -> date:
    """The local calendar date."""
    return datetime.now(UTC).astimezone().date()
