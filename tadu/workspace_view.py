"""The filter of a saved view named on the command line."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tadu.find_view import find_view
from tadu.load_workspace import load_workspace
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from tadu.card_filter import CardFilter


def workspace_view(workspace: str | None, name: str) -> CardFilter:
    """Return the named view of the workspace; without a workspace it is an error."""
    if workspace is None:
        msg = "--view needs --workspace"
        raise WorkspaceError(msg)
    return find_view(load_workspace(Path(workspace)), name)
