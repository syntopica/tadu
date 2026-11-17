"""Keys a `[[view]]` table of the workspace file may hold."""

from __future__ import annotations

VIEW_KEYS = frozenset(
    {
        "name",
        "project",
        "org",
        "role",
        "assignee",
        "column",
        "priority",
        "kind",
        "label",
        "due_before",
        "check_before",
        "include_cancelled",
        "open",
    }
)
