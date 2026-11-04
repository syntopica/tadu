"""Decide whether a closed log entry belongs on the board."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date


def is_recent_entry(day: date | None, since: date | None, cutoff: date) -> bool:
    """True for a dated entry on or after the cutoff and not before the log marker."""
    if day is None:
        return False
    if since is not None and day < since:
        return False
    return day >= cutoff
