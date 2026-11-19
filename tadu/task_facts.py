"""The keys of a task version that history reports one by one."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.task_field_kinds import TASK_LINE_KEYS
from tadu.task_key_order import TASK_KEY_ORDER
from tadu.task_object import task_object

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem

LAST = len(TASK_KEY_ORDER)


def task_facts(item: BacklogItem | None) -> dict[str, str | None]:
    """`file`, then each key of the task file in canonical order, then any other key by name.

    Values as text: lists joined with `, `, other JSON as JSON. The Markdown line keys (notes,
    done_when, evidence) are left to task_line_changes. A version that is not a JSON object
    reports that; no item (before the task was created) has no facts.
    """
    if item is None:
        return {}
    task = task_object(item.text)
    if task is None:
        return {"file": item.path, "text": "not a JSON object"}
    keys = sorted(
        (key for key in task if key not in TASK_LINE_KEYS),
        key=lambda key: (TASK_KEY_ORDER.index(key) if key in TASK_KEY_ORDER else LAST, key),
    )
    facts: dict[str, str | None] = {"file": item.path}
    for key in keys:
        value = task[key]
        shown = ", ".join(str(v) for v in value) if isinstance(value, list) else value
        # keys: the keys of one JSON object, each once
        facts[key] = shown if isinstance(shown, str) else json.dumps(shown, ensure_ascii=False)
    return facts
