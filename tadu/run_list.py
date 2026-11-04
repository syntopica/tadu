"""The list command."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from tadu.card_json import card_json
from tadu.card_matches import card_matches
from tadu.filter_from_args import filter_from_args
from tadu.format_card_line import format_card_line
from tadu.load_cards import load_cards
from tadu.print_problems import print_problems
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_list(args: argparse.Namespace, today: date) -> int:
    """Print the matching cards; problems go to stderr and do not change the exit code."""
    try:
        cards, problems, _ = load_cards(tuple(args.paths), args.workspace, args.done_days, today)
    except WorkspaceError as error:
        print(f"tadu list: {error}", file=sys.stderr)
        return 2
    card_filter = filter_from_args(args)
    for card in cards:
        if card_matches(card, card_filter):
            print(
                json.dumps(card_json(card), ensure_ascii=False)
                if args.json
                else format_card_line(card)
            )
    print_problems("list", problems)
    return 0
