"""The request handler of a board that signs people in with GitHub."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from tadu.authorize_post import authorize_post
from tadu.board_answer import BoardAnswer
from tadu.board_handler import BoardHandler
from tadu.board_operation_path import BOARD_OPERATION_PATH
from tadu.board_path import board_path
from tadu.board_post_paths import POST_PATHS
from tadu.client_address import client_address
from tadu.cookie_name import cookie_name
from tadu.host_refusal import host_refusal
from tadu.into_subfolder import into_subfolder
from tadu.json_error import json_error
from tadu.rate_limited import rate_limited
from tadu.request_cookies import request_cookies
from tadu.send_board_response import send_board_response
from tadu.session_check import session_check
from tadu.sign_in_settings import SESSION_COOKIE, SIGN_OUT_PATH
from tadu.sign_out import sign_out
from tadu.signed_in_call import signed_in_call
from tadu.team_route import team_route

if TYPE_CHECKING:
    from collections.abc import Callable

    from tadu.github_sign_in import GithubSignIn


class TeamBoardHandler(BoardHandler):
    """Checks Host, then answers by the session cookie instead of the token.

    GET as the board does, plus POST to sign out, to report activity and to call a tool
    (as the board does, if its --allow permits, on the repositories the person reads); a
    subclass binds `sign_in`.
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
        """GET, and POST to sign out, report activity on an open page or call a tool."""
        route = board_path(self.path, self.sign_in.base_path)
        posting = route in POST_PATHS or (route or "").startswith(BOARD_OPERATION_PATH)
        return self.command == "GET" or (self.command == "POST" and posting)

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

    @override
    def do_POST(self) -> None:
        """Sign out, run a tool call, or check the session with activity, which pushes its end back."""
        route = board_path(self.path, self.sign_in.base_path)
        if route == SIGN_OUT_PATH:
            self.answer(lambda cookies: sign_out(self.sign_in, cookies))
            return
        if route is not None and route.startswith(BOARD_OPERATION_PATH):
            self.answer(lambda cookies: self.call(route, cookies))
            return
        self.answer(
            lambda cookies: session_check(
                self.sign_in, cookies.get(cookie_name(self.sign_in, SESSION_COOKIE)), active=True
            )
        )

    def call(self, route: str, cookies: dict[str, str]) -> BoardAnswer:
        """Refuse a call that is not the board's page's; else run it for the session's person."""
        refusal = authorize_post(self.headers, self.state)
        if refusal is not None:
            return BoardAnswer(json_error(*refusal))
        body = self.rfile.read(int(self.headers["Content-Length"]))
        cookie = cookies.get(cookie_name(self.sign_in, SESSION_COOKIE))
        return signed_in_call(self.state, self.sign_in, cookie, (route, body))

    def answer(self, route: Callable[[dict[str, str]], BoardAnswer]) -> None:
        """421 for another Host, 403 for another page's request; else the route's answer.

        The 403 is cross_site_refusal's: the data or the session asked for by a page that
        is not the board's.
        """
        refusal = host_refusal(self.state.allowed_hosts, self.headers, self.sign_in, self.path)
        if refusal is not None:
            send_board_response(self, refusal)
            return
        answer = route(request_cookies(self.headers.get("Cookie")))
        send_board_response(self, answer.response, *answer.headers)
