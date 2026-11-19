"""The mark command on a TODO.md backlog."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.field_checks import FIELD_CHECKS
from tadu.first_problem import first_problem
from tadu.item_match import item_match
from tadu.mark_request import MarkRequest
from tadu.mark_states import MARK_STATES
from tadu.note_error import note_error
from tadu.plan_mark import plan_mark
from tadu.run_todo_change import run_todo_change

if TYPE_CHECKING:
    import argparse
    from datetime import date


def markdown_mark(
    args: argparse.Namespace, fields: tuple[tuple[str, str], ...], today: date
) -> int:
    """Refuse a field-like note or an invalid field value, then mark the item --id or --match names."""
    problem = first_problem(
        [
            note_error(args.note) if args.note is not None else None,
            *(FIELD_CHECKS[name](value.strip()) for name, value in fields),
        ]
    )
    if problem is not None:
        print(f"tadu mark: {problem}", file=sys.stderr)
        return 2
    match = item_match("mark", args, today)
    if match is None:
        return 2
    root = Path(args.path)
    marker = MARK_STATES[args.state] if args.state else None
    plan = lambda: plan_mark(root, match, MarkRequest(marker, args.note, fields))  # noqa: E731
    done = [*([args.state] if args.state else []), *(f"{name} {value}" for name, value in fields)]
    verbs = (f"would set {'; '.join(done)}", f"set {'; '.join(done)}")
    return run_todo_change(root, plan, verbs, write=args.write)
