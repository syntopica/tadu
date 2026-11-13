"""An optional boolean value of a table row."""

from __future__ import annotations

from tadu.workspace_error import WorkspaceError


def optional_flag(row: dict[str, object], table: str, key: str) -> bool:
    """Return the boolean at `key`, False when absent; a non-boolean value is an error."""
    value = row.get(key, False)
    if not isinstance(value, bool):
        msg = f"{table}: {key} must be true or false"
        raise WorkspaceError(msg)
    return value
