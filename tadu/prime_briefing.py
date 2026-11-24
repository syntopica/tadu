"""Render a bounded backlog briefing from already-loaded cards."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.format_card_line import format_card_line
from tadu.inbox_cards import inbox_cards
from tadu.next_cards import next_cards
from tadu.open_cards import open_cards
from tadu.prime_workflow import prime_workflow
from tadu.urgent_cards import urgent_cards

if TYPE_CHECKING:
    from datetime import date

    from tadu.card import Card


def prime_briefing(cards: tuple[Card, ...], person: str | None, today: date) -> str:
    """Show at most five next tasks and the counts and workflow for this backlog's format."""
    chosen = next_cards(cards, person, today)
    shown = 5
    lines = [
        f"Open: {len(open_cards(cards))} items.",
        f"Next for an agent ({len(chosen)}, `tadu next`):",
        *(f"  {format_card_line(card)}" for card in chosen[:shown]),
    ]
    if len(chosen) > shown:
        lines.append(f"  and {len(chosen) - shown} more")
    lines.extend(
        (
            f"Waiting on a person: {len(inbox_cards(cards, person, today))} (`tadu inbox`).",
            f"Urgent or due by tomorrow: {len(urgent_cards(cards, today, 1))} (`tadu urgent`).",
            "Workflow (every command is a dry run until --write):",
            *(
                f"- {line}"
                for line in prime_workflow(
                    tasks=any(card.item.path.startswith("todo/") for card in cards)
                )
            ),
        )
    )
    return "\n".join(lines)
