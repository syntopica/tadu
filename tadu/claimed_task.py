"""Build the task a claim writes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.claim_refusal import claim_refusal
from tadu.task_command_error import TaskCommandError
from tadu.task_strings import task_strings

if TYPE_CHECKING:
    import argparse
    from datetime import date
    from pathlib import Path

    from tadu.task_file import TaskFile


def claimed_task(
    todo: Path, old: TaskFile, args: argparse.Namespace, today: date
) -> dict[str, object]:
    """The task in progress for args.who, started today unless it already was.

    TaskCommandError when it may not be claimed; --force only overrides someone else's claim,
    never a blocked, deferred or closed task. With --force the claimer replaces the assignees.
    """
    refusal = claim_refusal(todo, old.task, args.who, today)
    if refusal and not (args.force and "in progress by" in refusal):
        msg = f"{old.path.stem}: {refusal}"
        raise TaskCommandError(msg)
    current = task_strings(old.task, "assignees")
    team = [args.who] if args.force else list(dict.fromkeys((*current, args.who)))
    task = {**old.task, "state": "in_progress", "assignees": team}
    task.setdefault("started", today.isoformat())
    return task
