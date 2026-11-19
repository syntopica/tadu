"""The task changes a mark makes in a task backlog."""

from __future__ import annotations

STATES = {"open": "pending", "in_progress": "in_progress", "blocked": "blocked"}
KEYS = {
    "Priority": "priority",
    "Assignees": "assignees",
    "Due": "due",
    "Not before": "defer_until",
    "Labels": "labels",
    "Queue": "queue",
    "Estimate": "estimate",
}


def mark_task_changes(
    state: str | None, note: str | None, fields: tuple[tuple[str, str], ...]
) -> list[str]:
    """`tadu set` changes for a mark: the state, the note, then each field.

    Blocked takes the note as its `blocker`; leaving blocked drops the blocker; any other note
    is added to the notes. The fields are those tasks have: mark refuses Kind and Check on
    before (see format_refusal).
    """
    changes = [f"state={STATES[state]}"] if state is not None else []
    if state is not None and state != "blocked":
        changes.append("blocker=")
    if note is not None:
        changes.append(f"blocker={note}" if state == "blocked" else f"notes+={note}")
    changes += [f"{KEYS[name]}={value}" for name, value in fields]
    return changes
