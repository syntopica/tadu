"""The show command."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from tadu.card_json import card_json
from tadu.load_cards import load_cards
from tadu.print_problems import print_problems
from tadu.reverse_relation_lines import reverse_relation_lines
from tadu.shown_card import shown_card
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_show(args: argparse.Namespace, today: date) -> int:
    """Print the card a key or unique task-id prefix names, with the relations pointing at it.

    Exit 1 when none matches or a prefix matches several tasks.
    """
    try:
        cards, problems, _ = load_cards(tuple(args.paths), args.workspace, args.done_days, today)
    except WorkspaceError as error:
        print(f"tadu show: {error}", file=sys.stderr)
        return 2
    print_problems("show", problems)
    first = shown_card(cards, args.key)
    if first is None:
        return 1
    if args.json:
        print(json.dumps(card_json(first), ensure_ascii=False))
        return 0
    print("\n".join((first.item.text, *reverse_relation_lines(first, cards))))
    return 0
