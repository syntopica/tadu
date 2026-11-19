"""Why `tadu add` cannot honour an option on a task backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def task_add_refusal(args: argparse.Namespace) -> str | None:
    """The reason, or None: every option given must land in the task, never be dropped.

    --not-before is format 2's defer_until, so the two may only agree; --no-id has no
    meaning, as every task has an id.
    """
    if args.no_id:
        return "--no-id: every task of a task backlog has an id"
    if args.not_before and args.defer_until and args.not_before != args.defer_until:
        return "--not-before and --defer-until are the same day here; give one"
    return None
