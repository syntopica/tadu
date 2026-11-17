"""Cut one page out of a list of cards."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.card import Card


def card_page(
    cards: tuple[Card, ...], offset: int, limit: int
) -> tuple[tuple[Card, ...], str | None]:
    """cards[offset:offset + limit] (limit 0 = all), and a note when more cards follow.

    The note tells an agent how many remain and how to get them, so a long answer is never
    cut short silently.
    """
    shown = cards[offset : offset + limit] if limit else cards[offset:]
    rest = len(cards) - offset - len(shown)
    if rest <= 0:
        return shown, None
    end = offset + len(shown)
    note = f"showing {offset + 1}-{end} of {len(cards)}; {rest} more: add --offset {end}, or narrow the filter"
    return shown, note
