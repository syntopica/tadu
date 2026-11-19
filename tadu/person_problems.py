"""Problems in how people refer to organizations and GitHub accounts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.duplicate_problems import duplicate_problems
from tadu.github_login_pattern import GITHUB_LOGIN_PATTERN

if TYPE_CHECKING:
    from tadu.workspace import Workspace


def person_problems(workspace: Workspace) -> list[str]:
    """Unknown organizations, malformed GitHub logins and a login given to two people.

    GitHub logins ignore case, so `Ana` and `ana` are the same account.
    """
    organizations = {o.id for o in workspace.organizations}
    logins = [p.github for p in workspace.people if p.github is not None]
    return [
        *(
            f"person {p.id}: unknown organization {p.organization}"
            for p in workspace.people
            if p.organization is not None and p.organization not in organizations
        ),
        *(
            f"person {p.id}: github must be a GitHub login, such as octocat"
            for p in workspace.people
            if p.github is not None and GITHUB_LOGIN_PATTERN.fullmatch(p.github) is None
        ),
        *duplicate_problems("person github", (login.lower() for login in logins)),
    ]
