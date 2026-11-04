"""Generate a fresh task ID."""

from __future__ import annotations

import uuid


def new_task_id() -> str:
    """`t-` followed by a random lowercase UUID4."""
    return f"t-{uuid.uuid4()}"
