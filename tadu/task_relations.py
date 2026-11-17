"""The relations a task stores."""

from __future__ import annotations

from tadu.task_field_kinds import TASK_ID_KEYS, TASK_ID_LIST_KEYS
from tadu.task_str import task_str
from tadu.task_strings import task_strings


def task_relations(task: dict[str, object]) -> tuple[tuple[str, str], ...]:
    """(key, target id) for every single and list relation of the task, in key order."""
    single = [(key, target) for key in TASK_ID_KEYS if (target := task_str(task, key))]
    listed = [(key, target) for key in TASK_ID_LIST_KEYS for target in task_strings(task, key)]
    return (*single, *listed)
