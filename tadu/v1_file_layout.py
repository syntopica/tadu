"""How a format 1 file splits into a header, items and text outside them."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class V1FileLayout:
    """The items (first line index, lines, `##` section), the unplaced lines, the header's end.

    An item's lines start with the prose its section holds before its first item, as an
    indented paragraph after the item line; unplaced lines are the indices of the non-blank
    lines no item holds, past the header, which ends at the first `##` heading or item.
    """

    items: tuple[tuple[int, tuple[str, ...], str | None], ...]
    unplaced: tuple[int, ...]
    header_end: int
