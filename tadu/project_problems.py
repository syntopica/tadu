"""Problems in how projects refer to repositories and organizations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.workspace import Workspace


def project_problems(workspace: Workspace) -> list[str]:
    """Unknown repositories, repositories in two projects and unknown role organizations."""
    repositories = {r.key for r in workspace.repositories}
    organizations = {o.id for o in workspace.organizations}
    owners: dict[str, list[str]] = {}
    problems: list[str] = []
    for project in workspace.projects:
        for key in project.repositories:
            if key not in repositories:
                problems.append(f"project {project.key}: unknown repository {key}")
            owners.setdefault(key, []).append(project.key)
        for role, org in project.roles:
            if org not in organizations:
                problems.append(
                    f"project {project.key}: role {role} names unknown organization {org}"
                )
    problems += [
        f"repository {key} is in two projects: {', '.join(keys)}"
        for key, keys in owners.items()
        if len(keys) > 1
    ]
    return problems
