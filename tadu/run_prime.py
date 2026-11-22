"""The prime command: a short briefing an agent reads before it works the backlog."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.attention_scope import attention_scope
from tadu.format_card_line import format_card_line
from tadu.inbox_cards import inbox_cards
from tadu.next_cards import next_cards
from tadu.open_cards import open_cards
from tadu.prime_workflow import prime_workflow
from tadu.print_problems import print_problems
from tadu.urgent_cards import urgent_cards
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date

SHOWN = 5


def run_prime(args: argparse.Namespace, today: date) -> int:
    """Print the open counts, the first tasks `next` gives, and the workflow's commands."""
    try:
        cards, problems, person = attention_scope(args, today)
    except WorkspaceError as error:
        print(f"tadu prime: {error}", file=sys.stderr)
        return 2
    chosen = next_cards(cards, person, today)
    waiting = len(inbox_cards(cards, person, today))
    urgent = len(urgent_cards(cards, today, 1))
    print(f"Open: {len(open_cards(cards))} items.")
    print(f"Next for an agent ({len(chosen)}, `tadu next`):")
    for card in chosen[:SHOWN]:
        print(f"  {format_card_line(card)}")
    if len(chosen) > SHOWN:
        print(f"  and {len(chosen) - SHOWN} more")
    print(f"Waiting on a person: {waiting} (`tadu inbox`).")
    print(f"Urgent or due by tomorrow: {urgent} (`tadu urgent`).")
    tasks = any(card.item.path.startswith("todo/") for card in cards)
    print("Workflow (every command is a dry run until --write):")
    for line in prime_workflow(tasks=tasks):
        print(f"- {line}")
    print_problems("prime", problems)
    return 0
