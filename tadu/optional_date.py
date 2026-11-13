"""An optional TOML date value of a table row."""

from __future__ import annotations

from datetime import date, datetime

from tadu.workspace_error import WorkspaceError


def optional_date(row: dict[str, object], table: str, key: str) -> date | None:
    """Return the local date at `key`, None when absent; anything else is an error."""
    value = row.get(key)
    if value is not None and (not isinstance(value, date) or isinstance(value, datetime)):
        msg = f"{table}: {key} must be a date such as 2026-12-31"
        raise WorkspaceError(msg)
    return value
