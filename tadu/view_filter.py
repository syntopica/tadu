"""The filter a `--view` option selects."""

from __future__ import annotations

from pathlib import Path

from tadu.card_filter import CardFilter
from tadu.find_view import find_view
from tadu.load_workspace import load_workspace
from tadu.workspace_error import WorkspaceError


def view_filter(workspace: str | None, view: str | None) -> CardFilter:
    """An empty filter without a view; a view needs a workspace, else WorkspaceError."""
    if view is None:
        return CardFilter()
    if workspace is None:
        msg = "--view needs --workspace"
        raise WorkspaceError(msg)
    return find_view(load_workspace(Path(workspace)), view)
