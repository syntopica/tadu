"""Whole days an item has been blocked."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date


def blocked_days(since: date | None, today: date) -> int | None:
    """Days from the blocked date to today, never negative; None when not known."""
    return None if since is None else max((today - since).days, 0)
