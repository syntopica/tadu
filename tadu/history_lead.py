"""A version of an item whose origin is still to be found."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HistoryLead:
    """The item was `text` in `path` at each of `tips`; the commit that made it so is older.

    `newer` is the commit of the change found just after it, None from the start.
    """

    path: str
    text: str
    tips: tuple[str, ...]
    newer: str | None = None
