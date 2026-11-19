"""Pick the one open item a close or a mark names."""

from __future__ import annotations

import sys

from tadu.fenced_lines import fenced_lines
from tadu.matching_items import matching_items


def select_item(lines: list[str], match: str | int, name: str) -> int | None:
    """The item's line index; None after listing the candidates when not exactly one matches.

    `match` is text found in the item's first line, or the index of that line (from its key).
    """
    fenced = fenced_lines(lines)
    if isinstance(match, int):
        found = [index for index in matching_items(lines, fenced, "") if index == match]
    else:
        found = matching_items(lines, fenced, match)
    if len(found) == 1:
        return found[0]
    what = f"line {match + 1}" if isinstance(match, int) else repr(match)
    print(f"{name}: {len(found)} open items match {what}", file=sys.stderr)
    for index in found or matching_items(lines, fenced, ""):
        print(f"  {index + 1}: {lines[index]}", file=sys.stderr)
    return None
