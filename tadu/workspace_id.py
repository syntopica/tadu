"""A short, non-secret identifier of a workspace, for per-workspace browser storage."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.workspace_digest import workspace_digest

if TYPE_CHECKING:
    from pathlib import Path


def workspace_id(workspace: str | Path) -> str:
    """The first 12 hex digits of the workspace digest."""
    return workspace_digest(workspace)[:12]
