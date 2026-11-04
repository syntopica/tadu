"""The show command."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from tadu.card_json import card_json
from tadu.load_cards import load_cards
from tadu.print_problems import print_problems
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_show(args: argparse.Namespace, today: date) -> int:
    """Print the first card whose key matches; exit 1 when none does."""
    try:
        cards, problems, _ = load_cards(tuple(args.paths), args.workspace, args.done_days, today)
    except WorkspaceError as error:
        print(f"tadu show: {error}", file=sys.stderr)
        return 2
    print_problems("show", problems)
    found = [card for card in cards if card.item.key == args.key]
    if not found:
        print(f"tadu show: no item {args.key}", file=sys.stderr)
        return 1
    if len(found) > 1:
        print(
            f"tadu show: {args.key} matches {len(found)} items; showing the first", file=sys.stderr
        )
    first = found[0]
    print(json.dumps(card_json(first), ensure_ascii=False) if args.json else first.item.text)
    return 0
