"""Find the open item a key names, for a change to TODO.md."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.args_scope import args_scope
from tadu.cards_by_key import cards_by_key
from tadu.load_cards import load_cards

if TYPE_CHECKING:
    import argparse
    from datetime import date

    from tadu.card import Card


def open_card(command: str, args: argparse.Namespace, today: date) -> Card | None:
    """The one open item --id names in the scope; None after saying why on stderr.

    The key is what `tadu list` gives over the same scope: an ID, or a k- key. The scope is
    the one `target_path` already read.
    """
    cards, _, _ = load_cards(args_scope(args), -1, today)
    found = cards_by_key(cards, args.id)
    if len(found) != 1:
        keys = "".join(f"\n  {card.item.key}" for card in found)
        print(f"tadu {command}: {len(found)} open items have key {args.id}{keys}", file=sys.stderr)
        return None
    return found[0]
