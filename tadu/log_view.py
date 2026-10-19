"""A log split into lines, with its fence flags and headings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LogView:
    """The lines, whether each is fenced, and each heading as (index, level, text)."""

    lines: list[str]
    fenced: list[bool]
    headings: list[tuple[int, int, str]]
