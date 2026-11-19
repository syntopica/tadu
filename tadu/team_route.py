"""Answer a GET to a board that signs in with GitHub."""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from tadu.board_answer import BoardAnswer
from tadu.board_data_path import BOARD_CHECK_PATH, BOARD_DATA_PATH
from tadu.board_route import board_route
from tadu.cookie_name import cookie_name
from tadu.finish_sign_in import finish_sign_in
from tadu.session_check import session_check
from tadu.sign_in_settings import CALLBACK_PATH, SESSION_COOKIE, SIGN_IN_PATH
from tadu.signed_in_cards import signed_in_cards
from tadu.start_sign_in import start_sign_in

if TYPE_CHECKING:
    from tadu.board_state import BoardState
    from tadu.github_sign_in import GithubSignIn

LOGIN_PAGE = "/login.html"


def team_route(
    path: str, cookies: dict[str, str], state: BoardState, sign_in: GithubSignIn
) -> BoardAnswer:
    """The sign-in routes; the cards and the page's check with a session; at / the sign-in page without one.

    The page's scripts and stylesheet need no session: they hold no backlog data.
    """
    route, _, query = path.partition("?")
    if route == SIGN_IN_PATH:
        return start_sign_in(sign_in)
    if route == CALLBACK_PATH:
        return finish_sign_in(sign_in, query, cookies)
    cookie = cookies.get(cookie_name(sign_in, SESSION_COOKIE))
    if route in {BOARD_CHECK_PATH, BOARD_DATA_PATH}:
        checking = route == BOARD_CHECK_PATH
        return (
            session_check(sign_in, cookie) if checking else signed_in_cards(state, sign_in, cookie)
        )
    if route == "/" and sign_in.sessions.find(cookie, time.time()) is None:
        route = LOGIN_PAGE
    return BoardAnswer(board_route(route, state, datetime.now(UTC).astimezone().date()))
