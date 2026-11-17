"""The urgent command: what needs attention now, by who acts."""

from __future__ import annotations

import sys
from datetime import timedelta
from typing import TYPE_CHECKING

from tadu.attention_scope import attention_scope
from tadu.print_problems import print_problems
from tadu.print_sections import print_sections
from tadu.urgent_cards import urgent_cards
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_urgent(args: argparse.Namespace, today: date) -> int:
    """Print the sections; stderr says so when nothing is urgent."""
    try:
        cards, problems, _ = attention_scope(args, today)
    except WorkspaceError as error:
        print(f"tadu urgent: {error}", file=sys.stderr)
        return 2
    found = urgent_cards(cards, today, args.days)
    print_sections(found, as_json=args.json)
    if not found:
        horizon = (today + timedelta(days=args.days)).isoformat()
        print(f"tadu urgent: nothing is urgent, high priority or due by {horizon}", file=sys.stderr)
    print_problems("urgent", problems)
    return 0
