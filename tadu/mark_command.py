"""The mark command: set an open item's state, with a note saying why."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.mark_states import MARK_STATES
from tadu.note_error import note_error
from tadu.plan_mark import plan_mark
from tadu.run_todo_change import run_todo_change

if TYPE_CHECKING:
    import argparse


def mark_command(args: argparse.Namespace) -> int:
    """Refuse a blank, multi-line or field-like value, and a block without its blocker."""
    root, note = Path(args.path), args.note
    values = [args.match, *([note] if note is not None else [])]
    problems = [
        "arguments must not be blank" if any(not value.strip() for value in values) else None,
        "arguments must be single lines"
        if any(len(f"{value}x".splitlines()) > 1 for value in values)
        else None,
        note_error(note) if note is not None else None,
        "--state blocked needs a --note naming the blocker"
        if args.state == "blocked" and note is None
        else None,
        None if root.is_dir() else f"{root}: not a directory",
    ]
    problem = next((item for item in problems if item is not None), None)
    if problem is not None:
        print(f"tadu mark: {problem}", file=sys.stderr)
        return 2
    plan = lambda: plan_mark(root, args.match, MARK_STATES[args.state], note)  # noqa: E731
    verbs = (f"would mark it {args.state}", f"marked {args.state}")
    return run_todo_change(root, plan, verbs, write=args.write)
