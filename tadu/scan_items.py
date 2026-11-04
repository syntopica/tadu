"""Scan a backlog's lines into items."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.build_backlog_item import build_backlog_item
from tadu.derived_key import derived_key
from tadu.fenced_lines import fenced_lines
from tadu.item_state_pattern import ITEM_STATE_PATTERN
from tadu.item_title import item_title

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem


def scan_items(
    lines: list[str], repository: str, path: str, states: str
) -> tuple[BacklogItem, ...]:
    """Every unfenced top-level item whose state marker is in states."""
    fenced = fenced_lines(lines)
    seen: dict[str, int] = {}
    items: list[BacklogItem] = []
    for index, line in enumerate(lines):
        match = None if fenced[index] else ITEM_STATE_PATTERN.match(line)
        if match is None:
            continue
        title = item_title(lines, fenced, index, match.group(3))
        occurrence = seen.get(title, 0)
        seen[title] = occurrence + 1
        if match.group(1) in states:
            key = derived_key(repository, path, title, occurrence)
            items.append(build_backlog_item(lines, fenced, match, (index, path, key, title)))
    return tuple(items)
