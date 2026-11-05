"""The feed command."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from tadu.card_json import card_json
from tadu.load_cards import load_cards
from tadu.print_problems import print_problems
from tadu.recently_done import recently_done
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_feed(args: argparse.Namespace, today: date) -> int:
    """Print the recent closed items as JSON lines; problems go to stderr only."""
    try:
        cards, problems, _ = load_cards(tuple(args.paths), args.workspace, args.done_days, today)
    except WorkspaceError as error:
        print(f"tadu feed: {error}", file=sys.stderr)
        return 2
    for card in recently_done(cards):
        print(json.dumps(card_json(card), ensure_ascii=False))
    print_problems("feed", problems)
    return 0
