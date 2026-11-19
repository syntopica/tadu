"""The days `tadu changes` reads."""

from __future__ import annotations

from datetime import date, timedelta

DEFAULT_DAYS = 14


def change_days(since: date | None, until: date | None, today: date) -> tuple[date, date]:
    """The first and last day, both included: today unless given, and 14 days before the last.

    ValueError when the first day is after the last.
    """
    last = until or today
    first = since or last - timedelta(days=DEFAULT_DAYS)
    if first > last:
        msg = f"since {first.isoformat()} is after until {last.isoformat()}"
        raise ValueError(msg)
    return first, last
