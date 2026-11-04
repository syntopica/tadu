"""ISO text of an optional date."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date


def iso_date(day: date | None) -> str | None:
    """The ISO form of the date, or None."""
    return day.isoformat() if day else None
