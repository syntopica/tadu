"""End a person's board session."""

from __future__ import annotations

import time
from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.board_answer import BoardAnswer
from tadu.cookie_name import cookie_name
from tadu.end_session import end_session
from tadu.set_cookie import set_cookie
from tadu.sign_in_settings import SESSION_COOKIE

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn


def sign_out(sign_in: GithubSignIn, cookies: dict[str, str]) -> BoardAnswer:
    """End the session, its GitHub token revoked, and delete its cookie."""
    end_session(sign_in, cookies.get(cookie_name(sign_in, SESSION_COOKIE)), time.time())
    return BoardAnswer(
        (HTTPStatus.OK, b"{}", "application/json; charset=utf-8"),
        (set_cookie(sign_in, SESSION_COOKIE, "", 0),),
    )
