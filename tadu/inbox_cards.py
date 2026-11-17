"""What waits on a person."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.card_section import card_section
from tadu.held_by import held_by
from tadu.is_deferred import is_deferred
from tadu.open_cards import open_cards

if TYPE_CHECKING:
    from datetime import date

    from tadu.card import Card


def inbox_cards(cards: tuple[Card, ...], person: str | None, today: date) -> list[tuple[str, Card]]:
    """(section, card): decisions, items whose check date or deadline has come, blocked tasks.

    A waiting item is chased and a later item checked once its `Check on:` date or
    its `Due:` deadline is today or past; any other item whose `Check on:` has come
    is checked too. A blocked task counts only when the person is named and assigned,
    since an unassigned one waits on its blocker. Items assigned only to others and
    items whose `Not before:` is ahead are left out.
    """
    found: list[tuple[str, Card]] = []
    for card in open_cards(cards):
        fields, section = card.item.fields, card_section(card)
        if not held_by(card, person) or is_deferred(card, today):
            continue
        checked = fields.check_on is not None and fields.check_on <= today
        overdue = fields.due is not None and fields.due <= today
        mine = person is not None and person in fields.assignees
        if section == "decide" or (section in ("chase", "check") and (checked or overdue)):
            found.append((section, card))
        elif section in ("do", "blocked") and checked:
            found.append(("check", card))
        elif section == "blocked" and mine:
            found.append((section, card))
    return found
