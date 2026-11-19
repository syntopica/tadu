"""Take a person back from GitHub and start their session."""

from __future__ import annotations

import hmac
import time
from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import parse_qs

from tadu.board_answer import BoardAnswer
from tadu.cookie_name import cookie_name
from tadu.end_session import end_session
from tadu.exchange_github_code import exchange_github_code
from tadu.github_user_login import github_user_login
from tadu.set_cookie import set_cookie
from tadu.sign_in_settings import SESSION_COOKIE, STATE_COOKIE
from tadu.text_response import text_response

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn


def finish_sign_in(sign_in: GithubSignIn, query: str, cookies: dict[str, str]) -> BoardAnswer:
    """Start a session for the person GitHub sends back, and redirect to the board.

    `state` must match the sign-in cookie's; the code is traded for a token, with the
    cookie's PKCE verifier, and the token for the login. A session the browser already
    held ends (its token revoked), so a copy of its cookie does not outlive signing in
    again. Failures
    answer a plain-text page. Either way the sign-in cookie goes: a state serves once.
    """
    params = {name: values[0] for name, values in parse_qs(query).items()}
    kept = cookies.get(cookie_name(sign_in, STATE_COOKIE), "")
    expected, _, verifier = kept.partition(".")
    given = params.get("state", "")
    spent = set_cookie(sign_in, STATE_COOKIE, "", 0)
    if not expected or not verifier or not hmac.compare_digest(given.encode(), expected.encode()):
        message = "Sign-in failed: the sign-in link expired or was opened in another browser."
        return BoardAnswer(text_response(HTTPStatus.BAD_REQUEST, message), (spent,))
    if "code" not in params:
        message = "Sign-in failed: GitHub did not sign you in."
        return BoardAnswer(text_response(HTTPStatus.FORBIDDEN, message), (spent,))
    grant = exchange_github_code(sign_in, params["code"], verifier)
    login = github_user_login(sign_in, grant.token) if grant is not None else None
    if grant is None or login is None:
        message = "Sign-in failed: GitHub did not confirm who you are. Try again."
        return BoardAnswer(text_response(HTTPStatus.BAD_GATEWAY, message), (spent,))
    now = time.time()
    end_session(sign_in, cookies.get(cookie_name(sign_in, SESSION_COOKIE)), now)
    cookie = sign_in.sessions.create(login, grant, now)
    return BoardAnswer(
        (HTTPStatus.FOUND, b"", "text/plain; charset=utf-8"),
        (
            ("Location", f"{sign_in.base_path}/"),
            set_cookie(sign_in, SESSION_COOKIE, cookie, sign_in.sessions.idle_timeout),
            spent,
        ),
    )
