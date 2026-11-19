"""The kinds of change `tadu changes` reports, in the order it groups them."""

from __future__ import annotations

CHANGE_EVENTS = (
    "closed",
    "cancelled",
    "reopened",
    "started",
    "blocked",
    "created",
    "migrated",
    "changed",
    "removed",
)
