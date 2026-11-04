"""The rows of one array-of-tables, or none when it is absent."""

from __future__ import annotations

from tadu.workspace_error import WorkspaceError


def table_rows(data: dict[str, object], table: str) -> list[dict[str, object]]:
    """Return the rows under `table`; anything but a list of tables is an error."""
    rows = data.get(table, [])
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        msg = f"{table}: must be an array of tables"
        raise WorkspaceError(msg)
    return rows
