"""The backlog directories a scope reads, by the label its items carry."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tadu.load_local_config import load_local_config
from tadu.load_workspace import load_workspace
from tadu.root_labels import root_labels

if TYPE_CHECKING:
    from tadu.scope import Scope


def scope_roots(scope: Scope) -> dict[str, Path]:
    """Label to resolved backlog directory: workspace keys, else the labels of `root_labels`.

    A workspace repository without a checkout path on this machine is left out.
    """
    if scope.workspace is None:
        return root_labels(scope.paths or (".",))
    directory = Path(scope.workspace)
    loaded = load_workspace(directory)
    local = load_local_config(directory, loaded)
    # keys: load_workspace rejects a repository key used twice.
    return {
        entry.key: (local.paths[entry.key] / entry.backlog).resolve()
        for entry in loaded.repositories
        if entry.key in local.paths
    }
