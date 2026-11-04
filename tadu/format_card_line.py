"""One-line text form of a card."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.card import Card


def format_card_line(card: Card) -> str:
    """Render `<repository>:<path>:<line> [<column>] <priority or -> <title>`."""
    item = card.item
    priority = item.fields.priority or "-"
    return f"{card.repository}:{item.path}:{item.line} [{card.column}] {priority} {item.title}"
