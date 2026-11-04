"""Reject top-level keys a workspace file does not define."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from pathlib import Path


def check_top_level_keys(data: dict[str, object], allowed: frozenset[str], path: Path) -> None:
    """Raise WorkspaceError naming every unknown top-level key or table."""
    unknown = sorted(set(data) - allowed)
    if unknown:
        msg = f"{path}: unknown top-level key {', '.join(unknown)}"
        raise WorkspaceError(msg)
