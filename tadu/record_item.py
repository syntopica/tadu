"""Rebuild a backlog item from its cache record."""

from __future__ import annotations

from typing import cast

from tadu.backlog_item import BacklogItem
from tadu.field_problem import FieldProblem
from tadu.item_fields import ItemFields
from tadu.task_extras import TaskExtras
from tadu.text_day import text_day

Shape = tuple[
    str,
    bool,
    str,
    int,
    int,
    str,
    str | None,
    str,
    str,
    tuple[str | None, str | None, list[str], str | None],
    tuple[list[str], str, int | None],
    list[tuple[int, str]],
    tuple[str | None, str | None, str | None],
    tuple[str | None, str | None, list[tuple[str, str]]],
]


def record_item(record: object) -> BacklogItem:
    """The item item_record wrote; a record of another shape raises TypeError or ValueError."""
    if not isinstance(record, list):
        raise TypeError(record)
    key, stable, path, line, end_line, state, closed, title, text, a, b, problems, c, d = cast(
        "Shape", tuple(record)
    )
    (item_id, priority, assignees, due), (labels, queue, estimate) = a, b
    (category, task_type, milestone), (defer_until, started, relations) = c, d
    return BacklogItem(
        key=key,
        stable=stable,
        path=path,
        line=line,
        end_line=end_line,
        state=state,
        day=text_day(closed),
        title=title,
        text=text,
        fields=ItemFields(
            id=item_id,
            priority=priority,
            assignees=tuple(assignees),
            due=text_day(due),
            labels=tuple(labels),
            queue=queue,
            estimate=estimate,
        ),
        problems=tuple(FieldProblem(at, message) for at, message in problems) if problems else (),
        extras=TaskExtras(
            category,
            task_type,
            milestone,
            text_day(defer_until),
            text_day(started),
            tuple((kind, target) for kind, target in relations) if relations else (),
        ),
    )
