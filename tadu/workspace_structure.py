"""The workspace's organizations, projects and repositories as the board needs them."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.workspace import Workspace


def workspace_structure(workspace: Workspace) -> dict[str, object]:
    """Display names and project membership in file order; roles as {role, org} pairs."""
    return {
        "organizations": [{"id": o.id, "name": o.name} for o in workspace.organizations],
        "projects": [
            {
                "key": p.key,
                "name": p.name,
                "repositories": list(p.repositories),
                "roles": [{"role": role, "org": org} for role, org in p.roles],
            }
            for p in workspace.projects
        ],
        "repositories": [{"key": r.key} for r in workspace.repositories],
    }
