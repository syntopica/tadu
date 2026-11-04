"""Validate a Queue field value."""

from __future__ import annotations

from tadu.queues import QUEUES


def check_queue_value(value: str) -> str | None:
    """A problem message, or None when the value is a known queue."""
    if value in QUEUES:
        return None
    return "Queue is not backlog or ready"
