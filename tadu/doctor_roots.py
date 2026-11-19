"""The repository roots doctor checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.refuse_mixed_scope import refuse_mixed_scope
from tadu.scope_root import scope_root
from tadu.scope_roots import scope_roots
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from tadu.scope import Scope


def doctor_roots(scope: Scope) -> tuple[str, ...]:
    """The roots given (default `.`), the one repository named, or every one of the workspace.

    A workspace that does not load has none: doctor reports it with the workspace's items.
    WorkspaceError for paths beside a workspace, or a repository not in the scope.
    """
    refuse_mixed_scope(scope)
    if scope.repository is not None:
        return (str(scope_root(scope)[1]),)
    if scope.workspace is None:
        return scope.paths or (".",)
    try:
        return tuple(str(root) for root in scope_roots(scope).values())
    except WorkspaceError:
        return ()
