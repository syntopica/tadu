"""Push a used session's end back."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from tadu.sign_in_settings import KEEP_ALIVE_SECONDS

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn


def keep_alive(sign_in: GithubSignIn, cookie: str, now: float) -> bool:
    """Give the session its whole idle timeout again; True when it did.

    That is when its end was last pushed back at least KEEP_ALIVE_SECONDS ago, or a tenth
    of a shorter idle timeout, so the cookie is then sent again with its new end. Done under the session's lock, on the
    session as saved, so it never undoes a token renewed meanwhile.
    """
    sessions = sign_in.sessions
    with sessions.lock(cookie):
        session = sessions.find(cookie, now)
        if session is None or session.expires - now > sessions.idle_timeout - min(
            KEEP_ALIVE_SECONDS, sessions.idle_timeout // 10
        ):
            return False
        sessions.save(cookie, replace(session, expires=int(now) + sessions.idle_timeout))
    return True
