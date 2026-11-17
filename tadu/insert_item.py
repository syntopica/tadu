"""Place a new item in the lines of TODO.md."""

from __future__ import annotations

from tadu.fenced_lines import fenced_lines
from tadu.markdown_headings import markdown_headings

SECTION_LEVEL = 2


def insert_item(lines: list[str], item: list[str], category: str | None) -> tuple[list[str], int]:
    """New lines and the item's line index: last in its `## category`, else at the end.

    A category without a heading gets a new `## category` at the end of the file.
    """
    end = len(lines)
    heading: list[str] = []
    if category is not None:
        headings = markdown_headings(lines, fenced_lines(lines))
        starts = [
            index for index, level, text in headings if level == SECTION_LEVEL and text == category
        ]
        if starts:
            later = [
                index
                for index, level, _ in headings
                if index > starts[0] and level <= SECTION_LEVEL
            ]
            end = later[0] if later else len(lines)
        else:
            heading = [f"## {category}", ""]
    head, tail = lines[:end], lines[end:]  # the tail starts at a heading, or is empty
    while head and not head[-1].strip():
        head.pop()
    gap = [""] if head else []
    body = [*head, *gap, *heading, *item]
    return [*body, "", *tail] if tail else [*body, ""], len(head) + len(gap) + len(heading)
