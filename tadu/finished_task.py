"""Complete the closed copy of a task whose close stopped before deleting the open one."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.closed_task import closed_task
from tadu.task_close_conflict import task_close_conflict
from tadu.task_command_error import TaskCommandError
from tadu.task_field_kinds import TASK_CLOSING_KEYS
from tadu.task_str import task_str
from tadu.task_strings import task_strings

if TYPE_CHECKING:
    import argparse
    from datetime import date
    from pathlib import Path

    from tadu.task_file import TaskFile

# what a close writes or may hold as closed; everything else an open copy must share
CLOSING_KEYS = frozenset({"state", "evidence", *TASK_CLOSING_KEYS})


def finished_task(
    copies: tuple[TaskFile, TaskFile], args: argparse.Namespace, day: date, todo: Path
) -> dict[str, object]:
    """The closed copy, completed by this close; TaskCommandError when they conflict.

    `copies` are the task's open file and its closed file.

    `tadu close` writes the closed copy first and deletes the open one second, so the closed
    copy is the record: its closed date, result and resolution stay. Evidence this close adds
    is appended, and a result that was only the default (the title) takes the one given.
    Another state, result, resolution or duplicate, or an open copy changed since, is refused,
    so nothing recorded is replaced.
    """
    opened, recorded = copies
    where = recorded.path.relative_to(todo.parent).as_posix()
    record = recorded.task
    if not recorded.writable:
        msg = f"{where}: written by a newer tadu format; this tool will not rewrite it"
        raise TaskCommandError(msg)
    changed = sorted(
        key
        for key in {*opened.task, *record} - CLOSING_KEYS
        if opened.task.get(key) != record.get(key)
    )
    if changed:
        msg = (
            f"{where} is the closed copy of a close that stopped halfway, and the open copy "
            f"differs from it in {', '.join(changed)}; merge them by hand, then delete the open one"
        )
        raise TaskCommandError(msg)
    wanted = closed_task(opened.task, args, day, todo)
    conflict = task_close_conflict(record, wanted, args)
    if conflict is not None:
        msg = f"already closed in {where} by a close that stopped halfway, {conflict} to finish it"
        raise TaskCommandError(msg)
    evidence = list(task_strings(record, "evidence"))
    evidence += [item for item in task_strings(wanted, "evidence") if item not in evidence]
    finished = {**record, "evidence": evidence} if evidence else dict(record)
    if args.result and task_str(record, "state") == "done":
        finished["result"] = args.result
    return finished
