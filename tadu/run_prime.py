"""The prime command: a short briefing an agent reads before it works the backlog."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.attention_scope import attention_scope
from tadu.prime_briefing import prime_briefing
from tadu.print_problems import print_problems
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_prime(args: argparse.Namespace, today: date) -> int:
    """Print the open counts, the first tasks `next` gives, and the workflow's commands."""
    try:
        cards, problems, person = attention_scope(args, today)
    except WorkspaceError as error:
        print(f"tadu prime: {error}", file=sys.stderr)
        return 2
    print(prime_briefing(cards, person, today))
    print_problems("prime", problems)
    return 0
