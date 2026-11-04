"""The GET-only request handler of the board server."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import TYPE_CHECKING, ClassVar, override

from tadu.authorize_request import authorize_request
from tadu.board_cookie import board_cookie
from tadu.board_headers import BOARD_HEADERS
from tadu.board_route import board_route
from tadu.json_error import json_error
from tadu.request_token import request_token
from tadu.send_board_response import send_board_response

if TYPE_CHECKING:
    from tadu.board_state import BoardState


class BoardHandler(BaseHTTPRequestHandler):
    """Checks Host, then the token, then routes; a subclass binds `state`."""

    state: ClassVar[BoardState]
    server_version = "tadu"
    sys_version = ""

    @override
    def parse_request(self) -> bool:
        """Refuse every method but GET before it is dispatched."""
        parsed = super().parse_request()
        if not parsed or self.command == "GET":
            return parsed
        refusal = json_error(HTTPStatus.METHOD_NOT_ALLOWED, "only GET")
        send_board_response(self, refusal, ("Allow", "GET"))
        return False

    def do_GET(self) -> None:
        """Authorize, then serve the page, an asset or the cards."""
        token = request_token(self.path, self.headers.get("Cookie"))
        refusal = authorize_request(self.headers.get("Host"), token, self.state)
        if refusal is not None:
            send_board_response(self, json_error(refusal, HTTPStatus(refusal).phrase.lower()))
            return
        route = self.path.partition("?")[0]
        response = board_route(route, self.state, datetime.now(UTC).astimezone().date())
        from_query = route == "/" and request_token(self.path, None) is not None
        extra = (("Set-Cookie", board_cookie(self.state.token)),) if from_query else ()
        send_board_response(self, response, *extra)

    @override
    def end_headers(self) -> None:
        """Add the security headers to every response, errors included."""
        for name, value in BOARD_HEADERS.items():
            self.send_header(name, value)
        super().end_headers()

    @override
    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        """Log through log_message with the status only."""
        self.log_message("%s", code)

    @override
    def log_error(self, format: str, *args: object) -> None:
        """Drop: the base messages can quote the raw request line, token included."""

    @override
    def log_message(self, format: str, *args: object) -> None:
        """Write method, path without its query string, and status to stderr."""
        path = getattr(self, "path", "").partition("?")[0]
        sys.stderr.write(f"{self.command} {path} {format % args}\n")
