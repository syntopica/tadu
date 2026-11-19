"""The task object of a task file version."""

from __future__ import annotations

import json


def task_object(text: str | None) -> dict[str, object] | None:
    """The text as a JSON object; None for no text or text that is not one."""
    try:
        task: object = json.loads(text) if text is not None else None
    except ValueError:
        return None
    return task if isinstance(task, dict) else None
