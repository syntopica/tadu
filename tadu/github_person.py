"""The workspace person behind a GitHub login."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.workspace import Workspace


def github_person(workspace: Workspace, login: str) -> str | None:
    """The id of the person whose `github` is the login, ignoring case, else None."""
    return next(
        (p.id for p in workspace.people if p.github and p.github.lower() == login.lower()),
        None,
    )
