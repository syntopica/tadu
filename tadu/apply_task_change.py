"""Apply one `key=value`, `key+=value`, `key-=value` or `key=` change to a task."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tadu.resolve_task_ids import resolve_task_ids
from tadu.task_command_error import TaskCommandError
from tadu.task_field_kinds import (
    TASK_ID_KEYS,
    TASK_ID_LIST_KEYS,
    TASK_LINE_KEYS,
    TASK_LIST_KEYS,
    TASK_MANAGED_KEYS,
)
from tadu.task_key_order import TASK_KEY_ORDER
from tadu.task_states import OPEN_TASK_STATES
from tadu.task_strings import task_strings

if TYPE_CHECKING:
    from pathlib import Path

CHANGE_PATTERN = re.compile(r"^([a-z_][a-z0-9_-]*?)(\+=|-=|=)(.*)$", re.DOTALL)


def apply_task_change(task: dict[str, object], change: str, todo: Path) -> dict[str, object]:
    """The task with the change applied; TaskCommandError for a change tadu set does not allow.

    Lists take comma-separated values, except the Markdown line fields (notes, done_when,
    evidence), where the value is one line. Relation values may be unique id prefixes.
    """
    match = CHANGE_PATTERN.match(change)
    if match is None:
        msg = f"{change!r}: write key=value, key+=value, key-=value or key="
        raise TaskCommandError(msg)
    key, operation, value = match.groups()
    if key in TASK_MANAGED_KEYS or (key not in TASK_KEY_ORDER and not key.startswith("x-")):
        msg = f"{key}: {'set by tadu itself' if key in TASK_MANAGED_KEYS else 'not a task key'}"
        raise TaskCommandError(msg)
    if key == "state" and value not in OPEN_TASK_STATES:
        msg = "state: use tadu close to close a task"
        raise TaskCommandError(msg)
    if key not in TASK_LIST_KEYS:
        if operation != "=":
            msg = f"{key} is not a list: use {key}=value"
            raise TaskCommandError(msg)
        single = resolve_task_ids(todo, [value])[0] if key in TASK_ID_KEYS and value else value
        return {**task, key: int(single) if key == "estimate" and single.isdigit() else single}
    parts = [value] if key in TASK_LINE_KEYS else [p.strip() for p in value.split(",") if p.strip()]
    items = resolve_task_ids(todo, parts) if key in TASK_ID_LIST_KEYS else parts
    current = list(task_strings(task, key))
    if operation == "+=":
        items = current + [item for item in items if key in TASK_LINE_KEYS or item not in current]
    elif operation == "-=":
        items = [item for item in current if item not in items]
    return {**task, key: items}
