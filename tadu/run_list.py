"""The list command."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.args_scope import args_scope
from tadu.card_page import card_page
from tadu.filter_from_args import filter_from_args
from tadu.history_days import history_days
from tadu.list_view import list_view
from tadu.load_cards import load_cards
from tadu.merge_filters import merge_filters
from tadu.print_card_lines import print_card_lines
from tadu.print_problems import print_problems
from tadu.query_from_args import query_from_args
from tadu.select_cards import select_cards
from tadu.short_keys import short_keys
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_list(args: argparse.Namespace, today: date) -> int:
    """Print the matching cards a page at a time; problems go to stderr and do not change the exit code."""
    done_days = history_days(today) if args.history else -1 if args.open else args.done_days
    try:
        cards, problems, _ = load_cards(args_scope(args), done_days, today)
        card_filter = filter_from_args(args)
        # shortcut: the view reads the workspace file a second time; pass the loaded workspace if it grows slow.
        if args.view is not None:
            card_filter = merge_filters(list_view(args), card_filter)
    except WorkspaceError as error:
        print(f"tadu list: {error}", file=sys.stderr)
        return 2
    query = query_from_args(args)
    selected = select_cards(cards, card_filter, query, today)
    keys = short_keys(tuple(card.item.key for card in cards))
    shown, note = card_page(selected, query.offset, query.limit)
    print_card_lines(shown, keys, as_json=args.json, compact=args.compact)
    if note:
        print(f"tadu list: {note}", file=sys.stderr)
    print_problems("list", problems)
    return 0
