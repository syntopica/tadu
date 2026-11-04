"""A mandatory string value of a table row."""

from __future__ import annotations

from tadu.workspace_error import WorkspaceError


def required_text(row: dict[str, object], table: str, key: str) -> str:
    """Return the string at `key`; a missing or non-string value is an error."""
    value = row.get(key)
    if not isinstance(value, str):
        msg = f"{table}: {key} must be a string"
        raise WorkspaceError(msg)
    return value
