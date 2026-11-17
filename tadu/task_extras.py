"""What a task backlog item carries beyond the tadu v1 fields."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date


@dataclass(frozen=True)
class TaskExtras:
    """Category, type, milestone, dates and relations; empty for a v1 item except its category.

    `relations` holds (key, target id) pairs such as ("blocked_by", "t-...").
    """

    category: str | None = None
    task_type: str | None = None
    milestone: str | None = None
    defer_until: date | None = None
    started: date | None = None
    relations: tuple[tuple[str, str], ...] = ()
