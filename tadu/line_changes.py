"""The lines of an item one change added and removed, apart from its title and fields."""

from __future__ import annotations

from difflib import ndiff
from typing import TYPE_CHECKING

from tadu.body_lines import body_lines
from tadu.task_line_changes import task_line_changes
from tadu.todo_layout import TASK_SUFFIX

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem


def line_changes(
    before: BacklogItem | None, after: BacklogItem
) -> tuple[tuple[str, str, str], ...]:
    """(`+` or `-`, field, line) in the item's order; blank lines are left out.

    A task file's lines are those of its notes, done_when and evidence, each its own field; a
    Markdown item's other lines belong to `text`. Across a migration the two versions are not
    alike, so none are reported.
    """
    task = after.path.endswith(TASK_SUFFIX)
    if task and before is not None and not before.path.endswith(TASK_SUFFIX):
        return ()
    if task:
        return task_line_changes(before, after)
    old = body_lines(before) if before else []
    diff = ndiff(old, body_lines(after))
    return tuple((line[0], "text", line[2:]) for line in diff if line[0] in "+-")
