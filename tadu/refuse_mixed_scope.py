"""Refuse roots given beside a workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from tadu.scope import Scope


def refuse_mixed_scope(scope: Scope) -> None:
    """WorkspaceError when the scope has both repository paths and a workspace."""
    if scope.workspace is not None and scope.paths:
        msg = "give repository paths or --workspace, not both"
        raise WorkspaceError(msg)
