"""Validate who did or recorded something."""

from __future__ import annotations

from tadu.actor_pattern import ACTOR_PATTERN


def check_task_actor(value: object) -> str | None:
    """A message unless the value is a person id or agent:<name>."""
    if isinstance(value, str) and ACTOR_PATTERN.match(value):
        return None
    return "must be a person id or agent:<name>"
