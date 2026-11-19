"""One line a history entry says was added or removed."""

from __future__ import annotations

from typing import TypedDict


class HistoryLine(TypedDict):
    """`+` or `-`, the field the line belongs to, and the line.

    A task file's lines belong to `notes`, `done_when` or `evidence`; a Markdown item's to `text`.
    """

    op: str
    field: str
    text: str
