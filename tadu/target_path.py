"""The backlog directory a change is made to."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tadu.access_allows import access_allows
from tadu.args_scope import args_scope
from tadu.load_workspace import load_workspace
from tadu.refuse_mixed_scope import refuse_mixed_scope
from tadu.scope_root import scope_root
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse


def target_path(args: argparse.Namespace, needed: str) -> str:
    """The one root given (default `.`), as given; else the repository the scope names.

    Through a workspace, the repository's `access` must allow `needed` (write or admin).
    WorkspaceError when the repository cannot be told, or may not be changed.
    """
    scope = args_scope(args)
    if scope.workspace is None and len(scope.paths) <= 1 and scope.repository is None:
        return scope.paths[0] if scope.paths else "."
    refuse_mixed_scope(scope)
    label, root = scope_root(scope)
    if scope.workspace is not None:
        entries = load_workspace(Path(scope.workspace)).repositories
        access = next(entry.access for entry in entries if entry.key == label)
        if not access_allows(access, needed):
            msg = f"repository {label} allows {access} only, and this needs {needed}"
            raise WorkspaceError(msg)
    return str(root)
