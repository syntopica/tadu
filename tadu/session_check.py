"""Answer a page's check that its GitHub session still holds."""

from __future__ import annotations

import json
import time
from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.board_answer import BoardAnswer
from tadu.json_error import json_error
from tadu.keep_alive import keep_alive
from tadu.set_cookie import set_cookie
from tadu.sign_in_settings import IDLE_WARNING_SECONDS, SESSION_COOKIE

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn


def session_check(
    sign_in: GithubSignIn, cookie: str | None, *, active: bool = False
) -> BoardAnswer:
    """200 with the session's seconds left while it lives; else 401 and the cookie deleted.

    The answer also says how long before the end the page warns (`warn`), and a 401
    says "signed out". A plain check (GET) asks GitHub nothing and does not push the
    session's end back: a page left open alone still ends after its idle timeout.
    `active` (POST: the person acted on the page since the last check) is activity,
    which pushes the end back as loading the board does, the cookie sent again then.
    """
    now = time.time()
    renewed = keep_alive(sign_in, cookie, now) if active and cookie else False
    session = sign_in.sessions.find(cookie, now)
    if session is None:
        return BoardAnswer(
            json_error(HTTPStatus.UNAUTHORIZED, "signed out"),
            (set_cookie(sign_in, SESSION_COOKIE, "", 0),),
        )
    left = {"ok": True, "remaining": int(session.expires - now), "warn": IDLE_WARNING_SECONDS}
    headers = (set_cookie(sign_in, SESSION_COOKIE, cookie or "", sign_in.sessions.idle_timeout),)
    return BoardAnswer(
        (HTTPStatus.OK, json.dumps(left).encode(), "application/json; charset=utf-8"),
        headers if renewed else (),
    )
