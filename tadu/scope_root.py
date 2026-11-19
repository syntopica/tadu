"""The one repository a change is made to."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tadu.repository_choices import repository_choices
from tadu.scope_roots import scope_roots
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from tadu.scope import Scope


def scope_root(scope: Scope) -> tuple[str, Path]:
    """The label and full path of the backlog directory to change; WorkspaceError when unsure.

    `scope.repository` is the label items carry (a workspace key, a directory name, or the
    full path of roots that share a name) or the absolute path of one backlog directory.
    Left out, the scope must hold exactly one directory. A directory name that more
    than one root has, or a relative path, never picks one.
    """
    roots, repository = scope_roots(scope), scope.repository
    distinct = set(roots.values())
    if repository is None and len(distinct) == 1:
        return next(iter(roots.items()))
    if repository is not None and repository in roots:
        return repository, roots[repository]
    path = Path(repository).expanduser() if repository is not None else None
    if path is not None and path.is_absolute() and path.resolve() in distinct:
        return next((label, root) for label, root in roots.items() if root == path.resolve())
    choices = repository_choices(roots)
    asked = "several repositories" if repository is None else f"no repository {repository}"
    msg = f"{asked}; give --repository as one of: {choices}"
    raise WorkspaceError(msg)
