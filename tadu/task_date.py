"""Read one date value of a task."""

from __future__ import annotations

from datetime import date

from tadu.is_real_date import is_real_date
from tadu.task_str import task_str


def task_date(task: dict[str, object], key: str) -> date | None:
    """The value as a date when it is a real YYYY-MM-DD date, else None."""
    value = task_str(task, key)
    return date.fromisoformat(value) if value is not None and is_real_date(value) else None
