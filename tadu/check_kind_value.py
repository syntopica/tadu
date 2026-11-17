"""Validate a Kind field value."""

from __future__ import annotations

from tadu.kinds import KINDS


def check_kind_value(value: str) -> str | None:
    """A problem message, or None when the value is a known kind."""
    if value in KINDS:
        return None
    return "Kind is not one of task, decision, waiting, later"
