"""Pick the one open item a close-by-ID request names."""

from __future__ import annotations

import sys

from tadu.fenced_lines import fenced_lines
from tadu.items_with_id import items_with_id


def select_item_by_id(lines: list[str], uid: str, name: str) -> int | None:
    """The item's line index; None after reporting when not exactly one open item has `uid`."""
    found = items_with_id(lines, fenced_lines(lines), uid)
    if len(found) == 1:
        return found[0]
    print(f"{name}: {len(found)} open items have ID {uid!r}", file=sys.stderr)
    for index in found:
        print(f"  {index + 1}: {lines[index]}", file=sys.stderr)
    return None
