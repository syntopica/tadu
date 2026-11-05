"""Local calendar date of a Unix time."""

from __future__ import annotations

from datetime import UTC, date, datetime


def local_date(stamp: int) -> date:
    """The date the Unix time falls on in the machine's time zone, as `today` is computed."""
    return datetime.fromtimestamp(stamp, UTC).astimezone().date()
