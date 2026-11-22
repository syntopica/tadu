"""Build the task a close writes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.resolve_task_ids import resolve_task_ids
from tadu.task_command_error import TaskCommandError
from tadu.task_states import OPEN_TASK_STATES
from tadu.task_str import task_str

if TYPE_CHECKING:
    import argparse
    from datetime import date
    from pathlib import Path


def closed_task(
    task: dict[str, object], args: argparse.Namespace, day: date, todo: Path
) -> dict[str, object]:
    """The task with its closing keys appended; nothing it held is removed.

    --evidence closes it as done (result: --result, else the title), --resolution as cancelled,
    --duplicate-of or --superseded-by as cancelled with that link and a resolution naming the
    task kept.
    """
    if task_str(task, "state") not in OPEN_TASK_STATES:
        msg = f"{task['id']} is already {task['state']}"
        raise TaskCommandError(msg)
    closed = {**task, "closed": day.isoformat()}
    for link, said in (("duplicate_of", "Duplicate of"), ("superseded_by", "Superseded by")):
        if getattr(args, link):
            kept = resolve_task_ids(todo, [getattr(args, link)])[0]
            reason = args.resolution or f"{said} {kept}."
            return {**closed, "state": "cancelled", "resolution": reason, link: kept}
    if args.resolution:
        return {**closed, "state": "cancelled", "resolution": args.resolution}
    result = args.result or task_str(task, "title")
    return {**closed, "state": "done", "result": result, "evidence": [args.evidence]}
