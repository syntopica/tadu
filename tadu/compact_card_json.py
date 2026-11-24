"""The list projection without the raw task document."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.card_json import card_json

if TYPE_CHECKING:
    from tadu.card import Card


def compact_card_json(card: Card) -> dict[str, object]:
    """Keep the full JSON contract's metadata and omit only its potentially large text."""
    return {key: value for key, value in card_json(card).items() if key != "text"}
