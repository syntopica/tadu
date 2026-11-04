"""The optional fields of a backlog item."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date


@dataclass(frozen=True)
class ItemFields:
    """Parsed field values; invalid or absent fields keep their defaults."""

    id: str | None = None
    priority: str | None = None
    assignees: tuple[str, ...] = ()
    due: date | None = None
    labels: tuple[str, ...] = ()
    queue: str = "backlog"
    estimate: int | None = None
