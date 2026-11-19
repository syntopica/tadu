"""The checked-out repositories whose items a board may change."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.access_allows import access_allows

if TYPE_CHECKING:
    from tadu.local_config import LocalConfig
    from tadu.workspace import Workspace


def writable_keys(allow: str, workspace: Workspace, local: LocalConfig) -> list[str]:
    """Keys where both the board's --allow and the repository's own access permit a write."""
    return [
        entry.key
        for entry in workspace.repositories
        if access_allows(allow, "write")
        and access_allows(entry.access, "write")
        and entry.key in local.paths
    ]
