"""The section an open card belongs to, by who has to act on it."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.card import Card

KIND_SECTIONS = {"decision": "decide", "waiting": "chase", "later": "check"}


def card_section(card: Card) -> str:
    """`decide`, `chase` or `check` by kind; any other item is `blocked` when `[!]`, else `do`."""
    kind = card.item.fields.kind
    if kind in KIND_SECTIONS:
        return KIND_SECTIONS[kind]
    return "blocked" if card.item.state == "!" else "do"
