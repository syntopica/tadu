"""The similar command."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.format_card_line import format_card_line
from tadu.history_days import history_days
from tadu.load_cards import load_cards
from tadu.print_problems import print_problems
from tadu.short_keys import short_keys
from tadu.similar_cards import similar_cards
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_similar(args: argparse.Namespace, today: date) -> int:
    """Print the open and closed items (of all time) most like the text, best first.

    Run it before adding an item; the agent decides whether one of them is the same work.
    """
    try:
        cards, problems, _ = load_cards(
            tuple(args.paths), args.workspace, -1 if args.open else history_days(today), today
        )
    except WorkspaceError as error:
        print(f"tadu similar: {error}", file=sys.stderr)
        return 2
    pool = tuple(card for card in cards if card.item.state in " ~!") if args.open else cards
    keys = short_keys(tuple(card.item.key for card in cards))
    for overlap, card in similar_cards(pool, args.text, args.limit):
        print(f"{overlap:.2f} {format_card_line(card, keys.get(card.item.key))}")
    print_problems("similar", problems)
    return 0
