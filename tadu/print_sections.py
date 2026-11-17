"""Print cards under the heading of who acts on them."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.card_json import card_json
from tadu.format_card_line import format_card_line
from tadu.section_titles import SECTION_TITLES

if TYPE_CHECKING:
    from tadu.card import Card


def print_sections(found: list[tuple[str, Card]], *, as_json: bool) -> None:
    """Sections in their fixed order, cards in the order given; JSON adds a `section` key."""
    first = True
    for section, title in SECTION_TITLES.items():
        cards = [card for name, card in found if name == section]
        if not cards:
            continue
        if as_json:
            for card in cards:
                print(json.dumps(card_json(card) | {"section": section}, ensure_ascii=False))
            continue
        print(("" if first else "\n") + title)
        first = False
        for card in cards:
            print(format_card_line(card))
