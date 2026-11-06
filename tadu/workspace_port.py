"""The port a workspace's board prefers, so its URL and browser storage survive restarts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.workspace_digest import workspace_digest

if TYPE_CHECKING:
    from pathlib import Path


def workspace_port(workspace: str | Path) -> int:
    """40000 plus the workspace digest modulo 10000."""
    return 40000 + int(workspace_digest(workspace), 16) % 10000
