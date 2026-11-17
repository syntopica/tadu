"""The change `tadu mark` makes to one item."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarkRequest:
    """The new state marker (None keeps the state), a closing note and fields to set."""

    marker: str | None
    note: str | None
    fields: tuple[tuple[str, str], ...] = ()
