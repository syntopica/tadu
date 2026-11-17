"""The non-empty strings of an iterable, each kept once, in first-seen order."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


def unique_in_order(values: Iterable[str]) -> list[str]:
    """Drop empty strings and repeats; the first occurrence keeps its place."""
    kept: list[str] = []
    for value in values:
        if value and value not in kept:
            kept.append(value)
    return kept
