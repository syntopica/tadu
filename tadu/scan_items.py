"""Scan a backlog's lines into items."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.build_backlog_item import build_backlog_item
from tadu.derived_key import derived_key
from tadu.fenced_lines import fenced_lines
from tadu.item_state_pattern import ITEM_STATE_PATTERN
from tadu.item_title import item_title

if TYPE_CHECKING:
    import re
    from collections.abc import Callable

    from tadu.backlog_item import BacklogItem


def scan_items(
    lines: list[str], repository: str, path: str, keep: Callable[[re.Match[str]], bool]
) -> tuple[BacklogItem, ...]:
    """Every unfenced top-level item whose first line `keep` accepts.

    `keep` sees the match of the item's first line (state marker, day), so an item it
    refuses is never parsed: the Done column of a log of 25,000 entries builds only the
    few hundred of the last days. Items refused still count for the keys derived from
    repeated titles, so every key is what it would be with all items built.
    """
    fenced = fenced_lines(lines)
    seen: dict[str, int] = {}
    items: list[BacklogItem] = []
    for index, line in enumerate(lines):
        match = None if fenced[index] else ITEM_STATE_PATTERN.match(line)
        if match is None:
            continue
        title = item_title(lines, fenced, index, match.group(3))
        occurrence = seen.get(title, 0)
        # keys: counts the items of each title; replacing the count is the point.
        seen[title] = occurrence + 1
        if keep(match):
            key = derived_key(repository, path, title, occurrence)
            items.append(build_backlog_item(lines, fenced, match, (index, path, key, title)))
    return tuple(items)
