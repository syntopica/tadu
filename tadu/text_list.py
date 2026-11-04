"""A list-of-strings value."""

from __future__ import annotations

from tadu.workspace_error import WorkspaceError


def text_list(value: object, table: str, key: str) -> tuple[str, ...]:
    """Return the strings in `value`; anything but a list of strings is an error."""
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        msg = f"{table}: {key} must be a list of strings"
        raise WorkspaceError(msg)
    return tuple(value)
