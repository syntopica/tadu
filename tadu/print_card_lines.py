"""Print cards as `list` does."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.card_json import card_json
from tadu.format_card_line import format_card_line

if TYPE_CHECKING:
    from collections.abc import Iterable

    from tadu.card import Card


def print_card_lines(cards: Iterable[Card], keys: dict[str, str], *, as_json: bool) -> None:
    """One line per card, with its short key from `keys`, or one JSON object per card."""
    for card in cards:
        print(
            json.dumps(card_json(card), ensure_ascii=False)
            if as_json
            else format_card_line(card, keys.get(card.item.key))
        )
