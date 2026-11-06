"""Problems in how saved views refer to projects, organizations and people."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.workspace import Workspace


def view_problems(workspace: Workspace) -> list[str]:
    """One message per view criterion naming something that is not registered."""
    known = {
        "project": {p.key for p in workspace.projects},
        "org": {o.id for o in workspace.organizations},
        "assignee": {p.id for p in workspace.people},
    }
    problems: list[str] = []
    for view in workspace.views:
        values = {
            "project": view.card_filter.project,
            "org": view.card_filter.org,
            "assignee": view.card_filter.assignee,
        }
        problems += [
            f"view {view.name}: unknown {kind} {value}"
            for kind, value in values.items()
            if value is not None and value not in known[kind]
        ]
    return problems
