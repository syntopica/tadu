"""Bring what is known about one session's access up to date, asking GitHub little."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.access_decision import access_decision
from tadu.ask_repositories import ask_repositories
from tadu.refresh_list import refresh_list
from tadu.sign_in_settings import ACCESS_SECONDS, RETRY_SECONDS
from tadu.warn_renamed import warn_renamed

if TYPE_CHECKING:
    from tadu.board_session import BoardSession
    from tadu.github_sign_in import GithubSignIn

ANSWERS = (HTTPStatus.OK, HTTPStatus.NOT_FOUND)


def refresh_access(
    sign_in: GithubSignIn, session: BoardSession, wanted: set[str], now: float
) -> None:
    """Bring the session's access up to date for the wanted repositories.

    The repository list is read when stale; then each wanted repository that the list
    does not hold and no fresh answer covers is asked about, and a rename it reveals is
    reported to the operator. Nothing is asked within RETRY_SECONDS of a failure, nor
    with no usable token. Raise SignedOutError on 401. The caller holds the session's
    `access.lock`.
    """
    store = sign_in.access
    access = store.for_session(session.id, now)
    token = session.token
    if token is None or now - access.failed_at < RETRY_SECONDS:
        return
    if now - access.listed_at >= ACCESS_SECONDS and not refresh_list(sign_in, access, token, now):
        return
    asked = sorted(name for name in wanted if access_decision(access, name, now) is None)
    answers = ask_repositories(sign_in, token, asked, access)
    for name, (status, repository_id, now_named) in answers.items():
        if status == HTTPStatus.OK:
            warn_renamed(store, name, now_named)
        if status in ANSWERS:
            # keys: each name was asked once.
            access.checks[name] = (status == HTTPStatus.OK, now, repository_id)
    failed = next((status for status, _, _ in answers.values() if status not in ANSWERS), None)
    access.failed, access.failed_at = failed, now if failed is not None else float("-inf")
