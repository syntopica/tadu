"""Read one text value of a task."""

from __future__ import annotations


def task_str(task: dict[str, object], key: str) -> str | None:
    """The value when it is a string, else None."""
    value = task.get(key)
    return value if isinstance(value, str) else None
