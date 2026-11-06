"""Look up a saved view by name."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from tadu.card_filter import CardFilter
    from tadu.workspace import Workspace


def find_view(workspace: Workspace, name: str) -> CardFilter:
    """Return the filter of the named view; an unknown name is an error listing the known ones."""
    for view in workspace.views:
        if view.name == name:
            return view.card_filter
    known = ", ".join(v.name for v in workspace.views) or "none"
    msg = f"unknown view {name} (known: {known})"
    raise WorkspaceError(msg)
