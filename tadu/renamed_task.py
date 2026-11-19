"""Give a task back the ids a migration lost, in its own id and in its relations."""

from __future__ import annotations

from tadu.task_field_kinds import TASK_ID_KEYS, TASK_ID_LIST_KEYS
from tadu.task_str import task_str
from tadu.without_note import without_note


def renamed_task(task: dict[str, object], lost: dict[str, str]) -> dict[str, object]:
    """The task with each lost id it holds replaced by the real one, and its stray `ID:` note gone.

    An older tadu left a lost `ID:` line in the task's notes as text; it goes with the blank line
    that separated it. Everything else stays as it is.
    """
    renamed = dict(task)
    own = task_str(task, "id") or ""
    renamed["id"] = lost.get(own, own)
    for key in TASK_ID_KEYS:
        target = task_str(task, key)
        if target in lost:
            # keys: the task's own relation keys
            renamed[key] = lost[target]
    for key in TASK_ID_LIST_KEYS:
        targets = task.get(key)
        if isinstance(targets, list):
            # keys: the task's own relation keys
            renamed[key] = [lost.get(t, t) if isinstance(t, str) else t for t in targets]
    notes = task.get("notes")
    if isinstance(notes, list):
        renamed["notes"] = without_note(notes, f"ID: {renamed['id']}")
    return renamed
