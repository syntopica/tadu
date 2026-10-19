"""Turn a backlog item into a dated closed-work entry."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.category_prefix_pattern import CATEGORY_PREFIX_PATTERN
from tadu.open_item_pattern import OPEN_ITEM_PATTERN
from tadu.required_log_labels import REQUIRED_LOG_LABELS

if TYPE_CHECKING:
    from tadu.closing import Closing


def render_log_entry(item: list[str], closing: Closing, section: str | None) -> list[str]:
    """The entry lines: the item's text and continuation kept, then Result and the proof line."""
    text = closing.title or OPEN_ITEM_PATTERN.sub("", item[0], count=1).strip()
    prefix = CATEGORY_PREFIX_PATTERN.match(text)
    if closing.category or prefix is None:
        bare = text[prefix.end() :] if prefix else text
        text = f"**{closing.category or section or 'General'}:** {bare}"
    lines = [f"- [{closing.state}] {closing.day.isoformat()} — {text}", *item[1:]]
    if closing.result:
        lines.append(f"  - Result: {closing.result}")
    lines.append(f"  - {REQUIRED_LOG_LABELS[closing.state][1]} {closing.proof}")
    return lines
