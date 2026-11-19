"""The workspace repositories one signed-in person can read on GitHub."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.access_decision import access_decision
from tadu.confirmed_repository import confirmed_repository
from tadu.github_repository import github_repository
from tadu.refresh_access import refresh_access
from tadu.repository_access import RepositoryAccess
from tadu.seen_repository_id import seen_repository_id
from tadu.sign_in_settings import RETRY_SECONDS

if TYPE_CHECKING:
    from tadu.board_session import BoardSession
    from tadu.github_sign_in import GithubSignIn
    from tadu.workspace import Workspace


def readable_repositories(
    sign_in: GithubSignIn, session: BoardSession, workspace: Workspace, now: float
) -> RepositoryAccess:
    """The repositories the session's token can read, as far as fresh answers say.

    A repository without a GitHub remote is never readable, one that nothing fresh says
    the token can read stays hidden, and one whose GitHub id is not its own is hidden.
    Answers are kept per session: its tabs share them, and one refresh per session runs
    at a time while the others wait. With no usable token (it expired and GitHub could
    not be reached to renew it), only answers still fresh count, and `failed` says
    GitHub could not be reached. Raise SignedOutError when GitHub refuses the token.
    """
    named = [(entry, github_repository(entry)) for entry in workspace.repositories]
    wanted = {name for _, name in named if name is not None}
    access = sign_in.access.for_session(session.id, now)
    with access.lock:
        if wanted:
            refresh_access(sign_in, session, wanted, now)
        failed = access.failed if now - access.failed_at < RETRY_SECONDS else None
        if session.token is None:
            failed = 0
        allowed = [
            (entry, name, seen_repository_id(access, name, now))
            for entry, name in named
            if name is not None and access_decision(access, name, now)
        ]
    confirmed = {
        entry.key
        for entry, name, seen in allowed
        if confirmed_repository(sign_in, entry, name, seen)
    }
    return RepositoryAccess(frozenset(confirmed), failed, len(confirmed) < len(allowed))
