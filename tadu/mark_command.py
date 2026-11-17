"""The mark command: set an open item's state and fields, with a note saying why."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.field_checks import FIELD_CHECKS
from tadu.mark_fields import MARK_FIELDS
from tadu.mark_request import MarkRequest
from tadu.mark_states import MARK_STATES
from tadu.note_error import note_error
from tadu.plan_mark import plan_mark
from tadu.run_todo_change import run_todo_change

if TYPE_CHECKING:
    import argparse


def mark_command(args: argparse.Namespace) -> int:
    """Refuse a blank, multi-line or field-like value, and a block without its blocker."""
    root, note = Path(args.path), args.note
    fields = tuple((name, getattr(args, flag)) for name, flag in MARK_FIELDS if getattr(args, flag))
    values = [args.match, *([note] if note is not None else []), *(value for _, value in fields)]
    problems = [
        "arguments must not be blank" if any(not value.strip() for value in values) else None,
        "arguments must be single lines"
        if any(len(f"{value}x".splitlines()) > 1 for value in values)
        else None,
        note_error(note) if note is not None else None,
        *(FIELD_CHECKS[name](value.strip()) for name, value in fields),
        "give --state or a field to set" if args.state is None and not fields else None,
        "--state blocked needs a --note naming the blocker"
        if args.state == "blocked" and note is None
        else None,
        None if root.is_dir() else f"{root}: not a directory",
    ]
    problem = next((item for item in problems if item is not None), None)
    if problem is not None:
        print(f"tadu mark: {problem}", file=sys.stderr)
        return 2
    marker = MARK_STATES[args.state] if args.state else None
    plan = lambda: plan_mark(root, args.match, MarkRequest(marker, note, fields))  # noqa: E731
    done = [*([args.state] if args.state else []), *(f"{name} {value}" for name, value in fields)]
    verbs = (f"would set {'; '.join(done)}", f"set {'; '.join(done)}")
    return run_todo_change(root, plan, verbs, write=args.write)
