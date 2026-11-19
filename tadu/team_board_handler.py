"""The request handler of a board that signs people in with GitHub."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, ClassVar, override

from tadu.board_data_path import BOARD_CHECK_PATH
from tadu.board_handler import BoardHandler
from tadu.board_path import board_path
from tadu.client_address import client_address
from tadu.cookie_name import cookie_name
from tadu.cross_site_refusal import cross_site_refusal
from tadu.into_subfolder import into_subfolder
from tadu.json_error import json_error
from tadu.rate_limited import rate_limited
from tadu.request_cookies import request_cookies
from tadu.send_board_response import send_board_response
from tadu.session_check import session_check
from tadu.sign_in_settings import SESSION_COOKIE, SIGN_OUT_PATH
from tadu.sign_out import sign_out
from tadu.team_route import team_route

if TYPE_CHECKING:
    from collections.abc import Callable

    from tadu.board_answer import BoardAnswer
    from tadu.github_sign_in import GithubSignIn


POST_PATHS = frozenset({SIGN_OUT_PATH, BOARD_CHECK_PATH})


class TeamBoardHandler(BoardHandler):
    """Checks Host, then answers by the session cookie instead of the token.

    GET as the board does, plus POST to sign out and to report activity; a subclass binds
    `sign_in`.
    """

    sign_in: ClassVar[GithubSignIn]

    @override
    def end_headers(self) -> None:
        """The board's headers; behind https, also HSTS: browsers then refuse plain http."""
        if self.sign_in.secure:
            self.send_header("Strict-Transport-Security", "max-age=31536000")
        super().end_headers()

    @override
    def allows(self) -> bool:
        """GET, and POST to sign out or to report activity on an open page."""
        posting = board_path(self.path, self.sign_in.base_path) in POST_PATHS
        return super().allows() or (self.command == "POST" and posting)

    @override
    def do_GET(self) -> None:
        """Serve the sign-in routes (each address only so often), the page, an asset or the cards.

        Paths are the board's own, with or without the subfolder the board is served in.
        """
        address = client_address(
            self.client_address[0], self.headers.get("X-Forwarded-For"), self.sign_in.proxy_hops
        )
        path = board_path(self.path, self.sign_in.base_path)
        if path is None:
            self.answer(lambda _cookies: into_subfolder(self.sign_in, self.path))
            return
        self.answer(
            lambda cookies: (
                rate_limited(self.sign_in, path, address)
                or team_route(path, cookies, self.state, self.sign_in)
            )
        )

    def do_POST(self) -> None:  # noqa: N802 - the name http.server dispatches POST to
        """Sign out, or check the session with activity, which pushes its end back."""
        if board_path(self.path, self.sign_in.base_path) == SIGN_OUT_PATH:
            self.answer(lambda cookies: sign_out(self.sign_in, cookies))
            return
        self.answer(
            lambda cookies: session_check(
                self.sign_in, cookies.get(cookie_name(self.sign_in, SESSION_COOKIE)), active=True
            )
        )

    def answer(self, route: Callable[[dict[str, str]], BoardAnswer]) -> None:
        """421 for another Host, 403 for another page's request; else the route's answer.

        The 403 is cross_site_refusal's: the data or the session asked for by a page that
        is not the board's.
        """
        if self.headers.get("Host") not in self.state.allowed_hosts:
            status = HTTPStatus.MISDIRECTED_REQUEST
            send_board_response(self, json_error(status, status.phrase.lower()))
            return
        path = board_path(self.path, self.sign_in.base_path)
        refusal = cross_site_refusal(self.state.allowed_hosts, path, self.headers)
        if refusal is not None:
            send_board_response(self, refusal)
            return
        answer = route(request_cookies(self.headers.get("Cookie")))
        send_board_response(self, answer.response, *answer.headers)
