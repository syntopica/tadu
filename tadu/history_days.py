"""How many days back reach the start of any history."""

from __future__ import annotations

from datetime import date


def history_days(today: date) -> int:
    """The --done-days value that includes every closed item ever, for --history."""
    return (today - date(1970, 1, 1)).days
