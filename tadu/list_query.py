"""The agent-facing criteria of the list command, beyond the card filter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import re


@dataclass(frozen=True)
class ListQuery:
    """Extra criteria, the sort order and the page; an empty set means "any"."""

    categories: frozenset[str] = frozenset()
    types: frozenset[str] = frozenset()
    milestone: str | None = None
    text: re.Pattern[str] | None = None
    due_within: int | None = None
    overdue: bool = False
    min_priority: str | None = None
    sort: str = "file"
    limit: int = 100
    offset: int = 0
