"""Validate an Assignees field value."""

from __future__ import annotations

from tadu.split_list_value import split_list_value


def check_assignees_value(value: str) -> str | None:
    """A problem message, or None when at least one assignee is named."""
    if split_list_value(value):
        return None
    return "Assignees is empty"
