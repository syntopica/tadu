"""The criteria a board card can be filtered by."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date  # noqa: TC003


@dataclass(frozen=True)
class CardFilter:
    """Optional criteria; every one that is set must hold.

    The MCP adapter builds its input schema from these annotations, so `date` is imported
    at runtime.
    """

    project: str | None = None
    org: str | None = None
    role: str | None = None
    assignee: str | None = None
    column: str | None = None
    priority: str | None = None
    label: str | None = None
    due_before: date | None = None
    include_cancelled: bool = False
