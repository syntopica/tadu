"""End a session on purpose: signing out, or signing in again over it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.revoke_github_token import revoke_github_token

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn


def end_session(sign_in: GithubSignIn, cookie: str | None, now: float) -> None:
    """Forget the cookie's session, on disk too, and have GitHub revoke its token.

    Sessions that end by themselves (the idle timeout, a full login) cannot be opened
    without their cookie, so their tokens are only forgotten.
    """
    session = sign_in.sessions.find(cookie, now)
    sign_in.sessions.drop(cookie)
    if session is not None and session.token is not None:
        revoke_github_token(sign_in, session.token)
