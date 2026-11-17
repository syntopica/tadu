"""The states of a task and the tadu v1 marker each one corresponds to."""

from __future__ import annotations

TASK_STATES = ("pending", "in_progress", "blocked", "done", "cancelled")
OPEN_TASK_STATES = ("pending", "in_progress", "blocked")
TASK_STATE_MARKERS = {
    "pending": " ",
    "in_progress": "~",
    "blocked": "!",
    "done": "x",
    "cancelled": "-",
}
