"""The claim command on a TODO.md backlog."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.claim_refusal import claim_refusal
from tadu.iso_date import iso_date
from tadu.mark_request import MarkRequest
from tadu.open_card import open_card
from tadu.plan_mark import plan_mark
from tadu.run_todo_change import run_todo_change

if TYPE_CHECKING:
    import argparse
    from datetime import date

STATES = {" ": "pending", "~": "in_progress", "!": "blocked"}


def markdown_claim(args: argparse.Namespace, today: date) -> int:
    """Mark the item --id names in progress, with --as among its assignees; exit 2 when refused.

    The item is refused as a task would be (see claim_refusal), its Not before: standing for
    defer_until; --force takes over someone else's item and makes --as its only assignee.
    """
    card = open_card("claim", args, today)
    if card is None:
        return 2
    fields, who = card.item.fields, args.who
    task: dict[str, object] = {
        "state": STATES[card.item.state],
        "assignees": list(fields.assignees),
        "defer_until": iso_date(fields.not_before),
    }
    refusal = claim_refusal(Path(args.path), task, who, today)
    if refusal is not None and not (args.force and "in progress by" in refusal):
        print(f"tadu claim: {card.item.key}: {refusal}", file=sys.stderr)
        return 2
    team = [who] if args.force else [*fields.assignees, *([] if who in fields.assignees else [who])]
    request = MarkRequest("~", None, (("Assignees", ", ".join(team)),))
    plan = lambda: plan_mark(Path(args.path), card.item.line - 1, request)  # noqa: E731
    verbs = (f"would claim for {who}", f"claimed for {who}")
    return run_todo_change(Path(args.path), plan, verbs, write=args.write)
