"""The ATX headings of a Markdown text, outside fences."""

from __future__ import annotations

import re

HEADING = re.compile(r"^(#{1,6}) (.*)$")


def markdown_headings(lines: list[str], fenced: list[bool]) -> list[tuple[int, int, str]]:
    """Each heading as (line index, level, stripped text)."""
    return [
        (index, len(match.group(1)), match.group(2).strip())
        for index, line in enumerate(lines)
        if not fenced[index] and (match := HEADING.match(line))
    ]
