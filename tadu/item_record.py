"""A backlog item as plain JSON values, for the item cache."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.iso_date import iso_date

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem


def item_record(item: BacklogItem) -> list[object]:
    """The item's values in a fixed order; record_item turns them back into the same item."""
    fields, extras = item.fields, item.extras
    return [
        item.key,
        item.stable,
        item.path,
        item.line,
        item.end_line,
        item.state,
        iso_date(item.day),
        item.title,
        item.text,
        [fields.id, fields.priority, list(fields.assignees), iso_date(fields.due)],
        [list(fields.labels), fields.queue, fields.estimate],
        [[problem.line, problem.message] for problem in item.problems],
        [extras.category, extras.task_type, extras.milestone],
        [
            iso_date(extras.defer_until),
            iso_date(extras.started),
            [list(r) for r in extras.relations],
        ],
    ]
