"""The title of a backlog item: its first paragraph joined into one line."""

from __future__ import annotations

from tadu.title_end import title_end


def item_title(lines: list[str], fenced: list[bool], first: int, text: str) -> str:
    """`text` plus each following indented line of the same paragraph, single-spaced."""
    rest = lines[first + 1 : title_end(lines, fenced, first)]
    return " ".join([text.strip(), *(line.strip() for line in rest)])
