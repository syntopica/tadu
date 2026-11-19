"""The workspace a scope names, loaded."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.load_local_config import load_local_config
from tadu.load_workspace import load_workspace
from tadu.refuse_mixed_scope import refuse_mixed_scope
from tadu.workspace_repository import workspace_repository

if TYPE_CHECKING:
    from tadu.local_config import LocalConfig
    from tadu.scope import Scope
    from tadu.workspace import Workspace


def scope_workspace(scope: Scope) -> tuple[Workspace, LocalConfig]:
    """The workspace and its local configuration, with only `scope.repository` when given.

    WorkspaceError when the workspace does not load, roots are given beside it, or it has no
    such repository.
    """
    refuse_mixed_scope(scope)
    directory = Path(str(scope.workspace))
    loaded = load_workspace(directory)
    local = load_local_config(directory, loaded)
    if scope.repository is not None:
        wanted = workspace_repository(scope, loaded)
        kept = tuple(entry for entry in loaded.repositories if entry.key == wanted)
        loaded = replace(loaded, repositories=kept)
    return loaded, local
