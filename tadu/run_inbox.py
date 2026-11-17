"""The inbox command: what waits on a person."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.attention_scope import attention_scope
from tadu.inbox_cards import inbox_cards
from tadu.next_cards import next_cards
from tadu.print_problems import print_problems
from tadu.print_sections import print_sections
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_inbox(args: argparse.Namespace, today: date) -> int:
    """Print the sections; stderr says when nothing waits and how much an agent could do."""
    try:
        cards, problems, person = attention_scope(args, today)
    except WorkspaceError as error:
        print(f"tadu inbox: {error}", file=sys.stderr)
        return 2
    found = inbox_cards(cards, person, today)
    print_sections(found, as_json=args.json)
    if not found:
        print(f"tadu inbox: nothing waits on {person or 'a person'}", file=sys.stderr)
    tasks = len(next_cards(cards, person, today))
    if tasks:
        print(
            f"tadu inbox: `tadu next` lists {tasks} task(s) an agent can do alone", file=sys.stderr
        )
    print_problems("inbox", problems)
    return 0
