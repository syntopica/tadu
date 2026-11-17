"""Read one list value of a task."""

from __future__ import annotations


def task_strings(task: dict[str, object], key: str) -> tuple[str, ...]:
    """The string elements of the value when it is a list, else an empty tuple."""
    value = task.get(key)
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str))
