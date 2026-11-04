"""Problems in how people refer to organizations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.workspace import Workspace


def person_problems(workspace: Workspace) -> list[str]:
    """One message per person naming an organization that is not registered."""
    organizations = {o.id for o in workspace.organizations}
    return [
        f"person {p.id}: unknown organization {p.organization}"
        for p in workspace.people
        if p.organization is not None and p.organization not in organizations
    ]
