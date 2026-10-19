"""Find a heading of one level whose text passes a test."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def first_heading(
    headings: list[tuple[int, int, str]], level: int, span: range, accept: Callable[[str], bool]
) -> int | None:
    """Line index of the first heading of `level` inside `span` whose text `accept`s."""
    for index, depth, text in headings:
        if depth == level and index in span and accept(text):
            return index
    return None
