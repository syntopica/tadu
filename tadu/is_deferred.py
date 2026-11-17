"""Whether an item may not be started yet."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from tadu.card import Card


def is_deferred(card: Card, today: date) -> bool:
    """True while its `Not before:` date is still ahead."""
    start = card.item.fields.not_before
    return start is not None and start > today
