"""The workspace repository a scope names."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.scope_root import scope_root

if TYPE_CHECKING:
    from tadu.scope import Scope
    from tadu.workspace import Workspace


def workspace_repository(scope: Scope, workspace: Workspace) -> str:
    """The key `scope.repository` names; WorkspaceError when it names none.

    A key of the workspace, checked out here or not, else one of its checkouts by full path
    (see scope_root).
    """
    keys = {entry.key for entry in workspace.repositories}
    return str(scope.repository) if scope.repository in keys else scope_root(scope)[0]
