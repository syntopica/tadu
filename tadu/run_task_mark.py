"""The mark command in a task backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.mark_task_changes import mark_task_changes
from tadu.run_task_change import run_task_change

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_task_mark(
    args: argparse.Namespace, fields: tuple[tuple[str, str], ...], today: date
) -> int:
    """Turn the mark into `tadu set` changes of the open task named; exit 2 when refused."""
    return run_task_change("mark", args, mark_task_changes(args.state, args.note, fields), today)
