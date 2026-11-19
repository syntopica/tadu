"""A task file as the item the board and the list commands show."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.backlog_item import BacklogItem
from tadu.field_problem import FieldProblem
from tadu.item_fields import ItemFields
from tadu.kinds import KINDS
from tadu.priorities import PRIORITIES
from tadu.relative_posix import relative_posix
from tadu.task_date import task_date
from tadu.task_extras import TaskExtras
from tadu.task_problems import task_problems
from tadu.task_relations import task_relations
from tadu.task_states import TASK_STATE_MARKERS
from tadu.task_str import task_str
from tadu.task_strings import task_strings

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.task_file import TaskFile


def task_item(file: TaskFile, root: Path) -> BacklogItem:
    """The item for one task; `root` is the repository checkout the path is shown relative to.

    An untriaged priority is shown as no priority, as in tadu v1; the text is the file itself.
    `defer_until` is the item's not-before day, so next, inbox and urgent leave it out until then.
    """
    task = file.task
    estimate = task.get("estimate")
    priority, kind = task_str(task, "priority"), task_str(task, "kind")
    fields = ItemFields(
        id=task_str(task, "id"),
        priority=priority if priority in PRIORITIES else None,
        assignees=task_strings(task, "assignees"),
        due=task_date(task, "due"),
        labels=task_strings(task, "labels"),
        queue=task_str(task, "queue") or "backlog",
        estimate=estimate if isinstance(estimate, int) and not isinstance(estimate, bool) else None,
        kind=kind if kind in KINDS else None,
        check_on=task_date(task, "check_on"),
        not_before=task_date(task, "defer_until"),
    )
    extras = TaskExtras(
        category=task_str(task, "category"),
        task_type=task_str(task, "type"),
        milestone=task_str(task, "milestone"),
        defer_until=task_date(task, "defer_until"),
        started=task_date(task, "started"),
        relations=task_relations(task),
    )
    return BacklogItem(
        key=task_str(task, "id") or file.path.stem,
        stable=True,
        path=relative_posix(file.path, root),
        line=1,
        end_line=file.text.count("\n") + (not file.text.endswith("\n")),
        state=TASK_STATE_MARKERS.get(task_str(task, "state") or "", " "),
        day=task_date(task, "closed"),
        title=task_str(task, "title") or "",
        text=file.text.rstrip("\n"),
        fields=fields,
        problems=tuple(FieldProblem(0, message) for message in task_problems(task)),
        extras=extras,
    )
