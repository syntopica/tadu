"""An optional string value of a table row."""

from __future__ import annotations

from tadu.workspace_error import WorkspaceError


def optional_text(row: dict[str, object], table: str, key: str) -> str | None:
    """Return the string at `key`, None when absent; a non-string value is an error."""
    value = row.get(key)
    if value is not None and not isinstance(value, str):
        msg = f"{table}: {key} must be a string"
        raise WorkspaceError(msg)
    return value
