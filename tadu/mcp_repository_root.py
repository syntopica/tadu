"""The one repository a writing tool changes."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tadu.scope_roots import scope_roots
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from tadu.mcp_scope import McpScope


def mcp_repository_root(scope: McpScope, repository: str | None) -> str:
    """The full path of the backlog directory to change; WorkspaceError when it is not certain.

    `repository` is the label items carry (a workspace key, a directory name, or the
    full path of roots that share a name) or the absolute path of one backlog directory.
    Left out, the server must read exactly one directory. A directory name that more
    than one root has, or a relative path, never picks one.
    """
    roots = scope_roots(scope)
    distinct = set(roots.values())
    if repository is None and len(distinct) == 1:
        return str(distinct.pop())
    if repository is not None and repository in roots:
        return str(roots[repository])
    path = Path(repository).expanduser() if repository is not None else None
    if path is not None and path.is_absolute() and path.resolve() in distinct:
        return str(path.resolve())
    choices = "; ".join(
        label if label == str(root) else f"{label} ({root})" for label, root in roots.items()
    )
    asked = "several repositories" if repository is None else f"no repository {repository}"
    msg = f"{asked}; give `repository` as one of: {choices}"
    raise WorkspaceError(msg)
