"""Narrow a workspace to what a person signed in with GitHub may see."""

from __future__ import annotations

import time
from dataclasses import replace
from typing import TYPE_CHECKING

from tadu.github_person import github_person
from tadu.payload_view import PayloadView
from tadu.readable_repositories import readable_repositories
from tadu.scan_problem import ScanProblem
from tadu.visible_workspace import visible_workspace

if TYPE_CHECKING:
    from tadu.board_session import BoardSession
    from tadu.github_sign_in import GithubSignIn
    from tadu.local_config import LocalConfig
    from tadu.workspace import Workspace


def signed_in_view(
    sign_in: GithubSignIn, session: BoardSession, workspace: Workspace, local: LocalConfig
) -> PayloadView:
    """The workspace cut to what the session's login reads on GitHub, and who `me` is.

    `me` is the person with that login; a problem says when some access could not be
    checked. Editor links are dropped: they point into this machine's checkouts.

    The problem names no repository, since the person may not be allowed to know it.
    Raise SignedOutError when GitHub refuses the token.
    """
    access = readable_repositories(sign_in, session, workspace, time.time())
    visible = visible_workspace(workspace, access.readable)
    problems: list[ScanProblem] = []
    if access.failed is not None:
        failed = access.failed
        why = "GitHub could not be reached" if failed == 0 else f"GitHub answered HTTP {failed}"
        message = f"{why}, so some repositories are hidden until Reload can check them"
        problems.append(ScanProblem("GitHub", message))
    if access.unconfirmed:
        message = (
            "a repository is hidden because the board cannot confirm it is still the same "
            "repository on GitHub; the board's operator has been told which"
        )
        problems.append(ScanProblem("GitHub", message))
    person = github_person(workspace, session.login)
    return PayloadView(
        visible, replace(local, me=person, editor_url=None), tuple(problems), session.login
    )
