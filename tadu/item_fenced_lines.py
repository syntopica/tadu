"""Which lines of one backlog item belong to a fenced code block."""

from __future__ import annotations

from tadu.fenced_lines import fenced_lines
from tadu.item_content_line import item_content_line


def item_fenced_lines(lines: list[str], fenced: list[bool], first: int, end: int) -> list[bool]:
    """The document flags, plus fences the item opens up to three spaces past its content indent.

    A fence indented four or five spaces is not one at document level, yet it is
    inside an item whose content starts at column two.
    """
    inner = fenced_lines([item_content_line(line) for line in lines[first + 1 : end]])
    return [
        flag or (first < index < end and inner[index - first - 1])
        for index, flag in enumerate(fenced)
    ]
