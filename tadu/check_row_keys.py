"""Reject keys a table row does not define."""

from __future__ import annotations

from tadu.workspace_error import WorkspaceError


def check_row_keys(row: dict[str, object], allowed: frozenset[str], table: str) -> None:
    """Raise WorkspaceError naming every unknown key of the row."""
    unknown = sorted(set(row) - allowed)
    if unknown:
        msg = f"{table}: unknown key {', '.join(unknown)}"
        raise WorkspaceError(msg)
