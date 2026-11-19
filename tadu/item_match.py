"""What names the item a change to TODO.md is made to."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.open_card import open_card

if TYPE_CHECKING:
    import argparse
    from datetime import date


def item_match(command: str, args: argparse.Namespace, today: date) -> str | int | None:
    """--match's text, else the 0-based line of the open item --id names (see open_card).

    None after saying on stderr that no single open item has that key.
    """
    if args.id is None:
        return str(args.match)
    card = open_card(command, args, today)
    return None if card is None else card.item.line - 1
