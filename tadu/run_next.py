"""The next command: what an agent can do now without a person."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from tadu.attention_scope import attention_scope
from tadu.card_json import card_json
from tadu.card_section import card_section
from tadu.format_card_line import format_card_line
from tadu.held_by import held_by
from tadu.is_deferred import is_deferred
from tadu.next_cards import next_cards
from tadu.open_cards import open_cards
from tadu.print_problems import print_problems
from tadu.section_counts import section_counts
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_next(args: argparse.Namespace, today: date) -> int:
    """Print the tasks; stderr says what else is open and where to find it."""
    try:
        cards, problems, person = attention_scope(args, today)
    except WorkspaceError as error:
        print(f"tadu next: {error}", file=sys.stderr)
        return 2
    chosen = next_cards(cards, person, today)
    for card in chosen:
        print(
            json.dumps(card_json(card), ensure_ascii=False) if args.json else format_card_line(card)
        )
    taken = {id(card) for card in chosen}
    rest = [card for card in open_cards(cards) if id(card) not in taken]
    others = sum(1 for card in rest if not held_by(card, person))
    later = sum(1 for card in rest if held_by(card, person) and is_deferred(card, today))
    mine = [card for card in rest if held_by(card, person) and not is_deferred(card, today)]
    parts = [section_counts([card_section(card) for card in mine])]
    parts += [f"{later} not before a later date"] if later else []
    parts += [f"{others} assigned to others"] if others else []
    left = ", ".join(part for part in parts if part)
    head = "" if chosen else "nothing an agent can do alone"
    if left:
        tail = f"not for an agent alone: {left} (`tadu inbox` lists what waits on a person now)"
        head = f"{head}; {tail}" if head else tail
    if head:
        print(f"tadu next: {head}", file=sys.stderr)
    print_problems("next", problems)
    return 0
