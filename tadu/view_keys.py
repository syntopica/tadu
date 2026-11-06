"""Keys a `[[view]]` row may hold."""

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
        "label",
        "due_before",
        "include_cancelled",
    }
)
