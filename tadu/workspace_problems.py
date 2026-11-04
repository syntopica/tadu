"""Check a workspace for duplicates and dangling references."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.duplicate_problems import duplicate_problems
from tadu.person_problems import person_problems
from tadu.project_problems import project_problems

if TYPE_CHECKING:
    from tadu.workspace import Workspace


def workspace_problems(workspace: Workspace) -> list[str]:
    """Every problem found, each naming the offending key."""
    return [
        *duplicate_problems("repository key", (r.key for r in workspace.repositories)),
        *duplicate_problems("organization id", (o.id for o in workspace.organizations)),
        *duplicate_problems("person id", (p.id for p in workspace.people)),
        *project_problems(workspace),
        *person_problems(workspace),
    ]
