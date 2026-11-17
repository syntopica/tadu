"""Existing tasks like a new title, as `tadu add` shows them first."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from tadu.build_cards import build_cards
from tadu.format_card_line import format_card_line
from tadu.read_task_items import read_task_items
from tadu.short_keys import short_keys
from tadu.similar_cards import similar_cards

if TYPE_CHECKING:
    from pathlib import Path

MIN_OVERLAP = 0.5


def similar_task_lines(root: Path, title: str) -> tuple[str, ...]:
    """Up to three open or closed tasks sharing at least half their words with the title.

    Shown, never blocking: deciding whether one is the same work is the agent's call.
    """
    items = read_task_items(root, ".", date.min)
    # path-name: a single root, so the folder name is only its display label
    cards = build_cards(items, root.resolve().name, root, None, None, None)
    keys = short_keys(tuple(item.key for item in items))
    return tuple(
        f"similar {overlap:.2f}: {format_card_line(card, keys[card.item.key])}"
        for overlap, card in similar_cards(cards, title, 3)
        if overlap >= MIN_OVERLAP
    )
