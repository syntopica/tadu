"""An optional string value limited to a fixed set."""

from __future__ import annotations

from tadu.optional_text import optional_text
from tadu.workspace_error import WorkspaceError


def optional_choice(
    row: dict[str, object], table: str, key: str, choices: tuple[str, ...]
) -> str | None:
    """Return the string at `key`, None when absent; a value outside `choices` is an error."""
    value = optional_text(row, table, key)
    if value is not None and value not in choices:
        msg = f"{table}: {key} must be one of {', '.join(choices)}"
        raise WorkspaceError(msg)
    return value
