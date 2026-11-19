"""The ready command."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.args_scope import args_scope
from tadu.card_page import card_page
from tadu.load_cards import load_cards
from tadu.print_card_lines import print_card_lines
from tadu.print_problems import print_problems
from tadu.ready_cards import ready_cards
from tadu.short_keys import short_keys
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_ready(args: argparse.Namespace, today: date) -> int:
    """Print what can be worked on now, a page at a time."""
    try:
        cards, problems, _ = load_cards(args_scope(args), -1, today)
    except WorkspaceError as error:
        print(f"tadu ready: {error}", file=sys.stderr)
        return 2
    keys = short_keys(tuple(card.item.key for card in cards))
    shown, note = card_page(ready_cards(cards, today), args.offset, args.limit)
    print_card_lines(shown, keys, as_json=args.json)
    if note:
        print(f"tadu ready: {note}", file=sys.stderr)
    print_problems("ready", problems)
    return 0
