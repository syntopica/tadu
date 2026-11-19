"""Print one card with its history, for `tadu show --history`."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from tadu.card_history import card_history
from tadu.card_json import card_json
from tadu.card_root import card_root
from tadu.filter_history import filter_history
from tadu.history_error import HistoryError
from tadu.history_filter_from_args import history_filter_from_args
from tadu.history_json import history_json
from tadu.history_lines import history_lines
from tadu.reverse_relation_lines import reverse_relation_lines

if TYPE_CHECKING:
    import argparse
    from datetime import date

    from tadu.card import Card
    from tadu.local_config import LocalConfig


def show_history(
    args: argparse.Namespace,
    card: Card,
    loaded: tuple[tuple[Card, ...], LocalConfig | None],
    today: date,
) -> int:
    """Print the card as `show` does, then each change, newest first; exit 1 without history.

    `loaded` is what the card was loaded with: every card and the workspace's local
    configuration. The history filters of the command line narrow the changes (see
    filter_history). With --json, the card's object gains a `history` list, and `shallow`.
    """
    cards, local = loaded
    try:
        events, shallow = card_history(card, card_root(tuple(args.paths), local, card.repository))
    except HistoryError as error:
        print(f"tadu show: {card.repository}: {error}", file=sys.stderr)
        return 1
    if shallow:
        print(
            f"tadu show: {card.repository} is a shallow clone; history stops at its oldest commit",
            file=sys.stderr,
        )
    entries = [history_json(event) for event in events]
    history = filter_history(entries, history_filter_from_args(args), today)
    if args.json:
        shown = {**card_json(card), "history": history, "shallow": shallow}
        print(json.dumps(shown, ensure_ascii=False))
        return 0
    print("\n".join((card.item.text, *reverse_relation_lines(card, cards))))
    for entry in history:
        print("\n" + "\n".join(history_lines(entry)))
    return 0
