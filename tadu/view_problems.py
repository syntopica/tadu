"""Problems in how saved views refer to projects, organizations and people."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.workspace import Workspace


def view_problems(workspace: Workspace) -> list[str]:
    """One message per view criterion naming something the workspace does not register."""
    known = {
        "project": {p.key for p in workspace.projects},
        "org": {o.id for o in workspace.organizations},
        "assignee": {p.id for p in workspace.people},
    }
    return [
        f"view {view.name}: unknown {field} {value}"
        for view in workspace.views
        for field, keys in known.items()
        if (value := getattr(view.card_filter, field)) is not None and value not in keys
    ]
