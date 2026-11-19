"""The facts of an item one change altered."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.item_facts import item_facts
from tadu.task_facts import task_facts
from tadu.todo_layout import TASK_SUFFIX

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem


def item_changes(
    before: BacklogItem | None, after: BacklogItem
) -> tuple[tuple[str, str | None, str | None], ...]:
    """(fact, before, after) for each fact that differs; every present fact of a new item.

    A task file (format v2) reports its keys, a Markdown item its fields. An item that became a
    task file when its backlog was migrated reports its new file and `format: 1 → 2`.
    """
    task = after.path.endswith(TASK_SUFFIX)
    if task and before is not None and not before.path.endswith(TASK_SUFFIX):
        return (("file", before.path, after.path), ("format", "1", "2"))
    facts = task_facts if task else item_facts
    old, new = facts(before), facts(after)
    keys = [*new, *(key for key in old if key not in new)]
    return tuple((key, old.get(key), new.get(key)) for key in keys if old.get(key) != new.get(key))
