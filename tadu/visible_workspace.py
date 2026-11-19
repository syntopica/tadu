"""The part of a workspace one person may see."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.workspace import Workspace


def visible_workspace(workspace: Workspace, readable: frozenset[str]) -> Workspace:
    """The workspace with only the readable repositories.

    It keeps the projects holding one, the organizations those projects name, and the
    saved views about nothing else; someone who reads none of the repositories (anyone
    with a GitHub account can sign in) gets no view either, so view names and criteria
    reach only people of the workspace's repositories. A project keeps only its readable repositories, so nothing names a hidden one.
    """
    projects = tuple(
        replace(p, repositories=tuple(key for key in p.repositories if key in readable))
        for p in workspace.projects
        if any(key in readable for key in p.repositories)
    )
    named = {org for project in projects for _, org in project.roles}
    project_keys = {p.key for p in projects}
    return replace(
        workspace,
        repositories=tuple(r for r in workspace.repositories if r.key in readable),
        projects=projects,
        organizations=tuple(o for o in workspace.organizations if o.id in named),
        views=tuple(
            v
            for v in workspace.views
            if readable
            and v.card_filter.project in {None, *project_keys}
            and v.card_filter.org in {None, *named}
        ),
    )
