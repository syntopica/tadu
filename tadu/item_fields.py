"""The optional fields of a backlog item."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date


@dataclass(frozen=True)
class ItemFields:
    """Parsed field values; invalid or absent fields keep their defaults.

    An item without `Kind:` is unclassified (`kind` None), never assumed to be a task.
    """

    id: str | None = None
    priority: str | None = None
    assignees: tuple[str, ...] = ()
    due: date | None = None
    check_on: date | None = None
    not_before: date | None = None
    labels: tuple[str, ...] = ()
    queue: str = "backlog"
    kind: str | None = None
    estimate: int | None = None
