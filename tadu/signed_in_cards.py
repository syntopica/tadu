"""The card data for the holder of a session cookie."""

from __future__ import annotations

import time
from datetime import UTC, datetime
from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.board_answer import BoardAnswer
from tadu.cards_response import cards_response
from tadu.json_error import json_error
from tadu.keep_alive import keep_alive
from tadu.renew_session import renew_session
from tadu.session_id import session_id
from tadu.set_cookie import set_cookie
from tadu.sign_in_settings import SESSION_COOKIE
from tadu.signed_in_view import signed_in_view
from tadu.signed_out_error import SignedOutError

if TYPE_CHECKING:
    from tadu.board_session import BoardSession
    from tadu.board_state import BoardState
    from tadu.github_sign_in import GithubSignIn
    from tadu.local_config import LocalConfig
    from tadu.payload_view import PayloadView
    from tadu.workspace import Workspace


def signed_in_cards(state: BoardState, sign_in: GithubSignIn, cookie: str | None) -> BoardAnswer:
    """The cards of the repositories the session's login reads on GitHub.

    The token is renewed when due; when GitHub refuses it anyway, it is renewed once
    more and the cards asked for again. A session in use has its end pushed back, and
    its cookie sent again with the new end. Without a live session, or when GitHub will
    not renew (which ends the session), 401 and the cookie deleted, so the page asks to
    sign in again.
    """
    now = time.time()
    today = datetime.now(UTC).astimezone().date()

    def cards(session: BoardSession) -> tuple[int, bytes, str]:
        def narrow(workspace: Workspace, local: LocalConfig) -> PayloadView:
            return signed_in_view(sign_in, session, workspace, local)

        return cards_response(state, today, narrow)

    if not cookie or sign_in.sessions.find(cookie, now) is None:
        return BoardAnswer(
            json_error(HTTPStatus.UNAUTHORIZED, "signed out"),
            (set_cookie(sign_in, SESSION_COOKIE, "", 0),),
        )
    try:
        try:
            response = cards(renew_session(sign_in, cookie, now))
        except SignedOutError:
            response = cards(renew_session(sign_in, cookie, now, force=True))
    except SignedOutError:
        sign_in.sessions.drop(cookie)
        sign_in.access.forget(session_id(cookie))
        return BoardAnswer(
            json_error(HTTPStatus.UNAUTHORIZED, "signed out"),
            (set_cookie(sign_in, SESSION_COOKIE, "", 0),),
        )
    renewed = keep_alive(sign_in, cookie, now)
    return BoardAnswer(
        response,
        (set_cookie(sign_in, SESSION_COOKIE, cookie, sign_in.sessions.idle_timeout),)
        if renewed
        else (),
    )
