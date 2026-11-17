"""Which task keys hold which kind of value."""

from __future__ import annotations

TASK_REQUIRED_KEYS = ("tadu", "id", "title", "state", "category", "type", "priority")
TASK_LINE_KEYS = ("notes", "done_when", "evidence")
TASK_LIST_KEYS = (
    "labels",
    "assignees",
    "blocked_by",
    "related",
    "notes",
    "done_when",
    "links",
    "evidence",
    "files",
)
TASK_ID_KEYS = ("parent", "discovered_from", "superseded_by", "duplicate_of")
TASK_ID_LIST_KEYS = ("blocked_by", "related")
TASK_CLOSING_KEYS = ("closed", "result", "resolution", "superseded_by", "duplicate_of")
TASK_MANAGED_KEYS = ("tadu", "id", "started", "closed")
