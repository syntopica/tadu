"""One fact a history entry says changed."""

from __future__ import annotations

from typing import TypedDict


class HistoryChange(TypedDict):
    """The field's name and its text before and after; None where absent."""

    field: str
    before: str | None
    after: str | None
