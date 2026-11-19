"""The canonical order of the keys of a task file.

Identity, classification, planning, relations and description come first and the closing keys
last, so closing a task only appends lines and merges with edits made on other branches.
"""

from __future__ import annotations

TASK_KEY_ORDER = (
    "tadu",
    "id",
    "title",
    "state",
    "category",
    "type",
    "priority",
    "kind",
    "labels",
    "milestone",
    "created",
    "created_by",
    "started",
    "due",
    "defer_until",
    "check_on",
    "queue",
    "assignees",
    "estimate",
    "parent",
    "blocked_by",
    "related",
    "discovered_from",
    "blocker",
    "unblock",
    "notes",
    "done_when",
    "links",
    "closed",
    "result",
    "evidence",
    "resolution",
    "superseded_by",
    "duplicate_of",
    "files",
)
