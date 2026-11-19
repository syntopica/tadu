"""Which lost IDs cannot be given back, and why."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.task_str import task_str

if TYPE_CHECKING:
    from collections.abc import Callable

    from tadu.task_file import TaskFile


def refused_recoveries(
    files: tuple[TaskFile, ...],
    lost: dict[str, str],
    finished: Callable[[TaskFile, TaskFile], bool],
) -> dict[str, str]:
    """Lost id -> why its task file cannot take its real ID back.

    Another task file has the real ID (unless `finished(wrong, right)` says it is what this
    file becomes: a run that stopped between writing it and removing the old one), several
    files share one of the ids (doctor's J007), the file is not named by its id (J005), or a
    newer tadu wrote it.
    """
    ids = [task_str(file.task, "id") for file in files]
    by_id = {task_str(file.task, "id"): file for file in files}  # keys: repeats are refused
    refused: dict[str, str] = {}
    for wrong_id, real_id in lost.items():
        wrong, right = by_id.get(wrong_id), by_id.get(real_id)
        if wrong is None:
            continue
        # path-name: a task file is named by its id, which J005 checks
        if ids.count(wrong_id) > 1 or ids.count(real_id) > 1 or wrong.path.stem != wrong_id:
            reason = "; fix doctor's J005 or J007 first"
        elif not wrong.writable:
            reason = "; written by a newer tadu format"
        elif right and not finished(wrong, right):
            reason = f", which {right.path} has; merge by hand"
        else:
            continue
        # keys: the lost ids, each a key of `lost` once
        refused[wrong_id] = f"{wrong.path}: was {real_id}{reason}"
    return refused
