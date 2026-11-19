"""Every task a backlog has once everything its format 1 files hold is in it, in memory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.canonical_task_text import canonical_task_text
from tadu.converted_tasks import converted_tasks
from tadu.merged_items import merged_items
from tadu.recovered_ids import recovered_ids
from tadu.refused_recoveries import refused_recoveries
from tadu.renamed_task import renamed_task
from tadu.renamed_tasks import renamed_tasks

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.task_file import TaskFile

Current = dict[str, tuple["TaskFile | None", dict[str, object]]]


def completed_tasks(
    files: tuple[TaskFile, ...], texts: dict[str, str], *, everything: bool
) -> tuple[Current, list[tuple[TaskFile, Path, None]], list[str]]:
    """(task id -> (its file or None when new, the task)), stale files, and what is refused.

    Tasks take back the IDs an older migrate lost (recovered_ids), then each converted item
    merges into its task. An item whose task is missing gets one when `everything`, else
    only a block of loose text, which an older migrate never made a task of.
    """
    lost, converted = recovered_ids(texts), converted_tasks(texts)
    items: dict[str, list[dict[str, object]]] = {}
    for task, _, _ in converted:
        items.setdefault(str(task["id"]), []).append(task)
    refused = refused_recoveries(
        files,
        lost,
        lambda wrong, right: (
            canonical_task_text(right.task)
            == canonical_task_text(
                merged_items(renamed_task(wrong.task, lost), items, everything=everything)
            )
        ),
    )
    renamed, stale = renamed_tasks(
        files, {wrong: real for wrong, real in lost.items() if wrong not in refused}
    )
    current: Current = dict(renamed)
    blocked = {real for wrong, real in lost.items() if wrong in refused}
    for task, _, loose in converted:
        task_id = str(task["id"])
        known = current.get(task_id)
        if known is not None:
            # keys: the ids of the backlog's tasks
            current[task_id] = (known[0], merged_items(known[1], items, everything=everything))
        elif task_id not in blocked and (everything or loose):
            # keys: the ids of the backlog's tasks
            current[task_id] = (None, task)
    return current, stale, list(refused.values())
