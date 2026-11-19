"""What part of an item's history to show."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date


@dataclass(frozen=True)
class HistoryFilter:
    """Fields whose changes to keep (none: all), the first and last day, and a part of the author.

    Days are inclusive and compared with the commit's day; uncommitted changes count as today.
    """

    fields: frozenset[str] = frozenset()
    since: date | None = None
    until: date | None = None
    author: str | None = None
