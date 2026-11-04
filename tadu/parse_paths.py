"""Resolve the [paths] table of the local configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.workspace import Workspace


def parse_paths(value: object, directory: Path, workspace: Workspace) -> dict[str, Path]:
    """Map each known repository key to its path under `directory`."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        msg = "paths: must be a table"
        raise WorkspaceError(msg)
    known = {r.key for r in workspace.repositories}
    paths: dict[str, Path] = {}
    for key, path in value.items():
        if key not in known:
            msg = f"paths: unknown repository {key}"
            raise WorkspaceError(msg)
        if not isinstance(path, str):
            msg = f"paths: {key} must be a string"
            raise WorkspaceError(msg)
        paths[key] = directory / path
    return paths
