"""The show command."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from tadu.args_scope import args_scope
from tadu.card_json import card_json
from tadu.history_days import history_days
from tadu.history_filter import HistoryFilter
from tadu.history_filter_from_args import history_filter_from_args
from tadu.load_cards import load_cards
from tadu.print_problems import print_problems
from tadu.reverse_relation_lines import reverse_relation_lines
from tadu.show_history import show_history
from tadu.shown_card import shown_card
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_show(args: argparse.Namespace, today: date) -> int:
    """Print the card a key or unique task-id prefix names, with the relations pointing at it.

    With --history, or any history filter, closed items of any age are found and each change
    git recorded follows (see show_history). Exit 1 when none matches, a prefix matches several tasks, or the
    history cannot be read.
    """
    wanted = history_filter_from_args(args)
    history = args.history or wanted != HistoryFilter()
    done_days = history_days(today) if history else args.done_days
    try:
        cards, problems, local = load_cards(args_scope(args), done_days, today)
    except WorkspaceError as error:
        print(f"tadu show: {error}", file=sys.stderr)
        return 2
    print_problems("show", problems)
    first = shown_card(cards, args.key)
    if first is None:
        return 1
    if history:
        return show_history(args, first, (cards, local), today)
    if args.json:
        print(json.dumps(card_json(first), ensure_ascii=False))
    else:
        print("\n".join((first.item.text, *reverse_relation_lines(first, cards))))
    return 0
