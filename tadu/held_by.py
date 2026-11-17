"""Whether an item is a person's to act on."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.card import Card


def held_by(card: Card, person: str | None) -> bool:
    """True with no person given, for an unassigned item, or when the person is assigned."""
    assignees = card.item.fields.assignees
    return person is None or not assignees or person in assignees
