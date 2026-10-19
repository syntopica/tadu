"""Pick the one open item a close request names."""

from __future__ import annotations

import sys

from tadu.fenced_lines import fenced_lines
from tadu.matching_items import matching_items


def select_item(lines: list[str], match: str, name: str) -> int | None:
    """The item's line index; None after listing the candidates when not exactly one matches."""
    fenced = fenced_lines(lines)
    found = matching_items(lines, fenced, match)
    if len(found) == 1:
        return found[0]
    print(f"{name}: {len(found)} open items match {match!r}", file=sys.stderr)
    for index in found or matching_items(lines, fenced, ""):
        print(f"  {index + 1}: {lines[index]}", file=sys.stderr)
    return None
