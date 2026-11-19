"""Give a session a GitHub token fit to use, renewing it when it is due."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from tadu.refresh_github_token import refresh_github_token
from tadu.signed_out_error import SignedOutError
from tadu.token_due import token_due

if TYPE_CHECKING:
    from tadu.board_session import BoardSession
    from tadu.github_sign_in import GithubSignIn


def renew_session(
    sign_in: GithubSignIn, cookie: str, now: float, *, force: bool = False
) -> BoardSession:
    """The cookie's session, its token renewed when due.

    With `force`, it is renewed because GitHub just refused it. One request per session
    renews at a time, under the session's lock; the others then find the new token and
    use it, since GitHub takes each refresh token only once. When GitHub cannot be
    reached to renew, the session goes on: with its token while that has not expired
    (and GitHub did not just refuse it), else with none for this request. Raise
    SignedOutError when the session ended or GitHub will not renew: its authorization
    was revoked, or the refresh token expired.
    """
    sessions = sign_in.sessions
    seen = sessions.find(cookie, now)
    if seen is None:
        raise SignedOutError
    if not force and not token_due(seen, now):
        return seen
    with sessions.lock(cookie):
        current = sessions.find(cookie, now)
        if current is None or current.refresh_token is None:
            raise SignedOutError
        if current.token is not None and current.token != seen.token:
            return current
        grant = refresh_github_token(sign_in, current.refresh_token)
        if grant is None:
            expires = current.token_expires
            still_works = not force and (expires is None or expires > now)
            return current if still_works else replace(current, token=None)
        renewed = replace(
            current,
            token=grant.token,
            token_expires=grant.expires,
            refresh_token=grant.refresh_token or current.refresh_token,
        )
        sessions.save(cookie, renewed)
        return renewed
