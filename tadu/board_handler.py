"""The request handler of the board server."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import TYPE_CHECKING, ClassVar, override

from tadu.authorize_post import authorize_post
from tadu.authorize_request import authorize_request
from tadu.board_call import board_call
from tadu.board_data_path import BOARD_CHECK_PATH
from tadu.board_headers import BOARD_HEADERS
from tadu.board_route import board_route
from tadu.json_error import json_error
from tadu.request_token import request_token
from tadu.send_board_response import send_board_response

if TYPE_CHECKING:
    from tadu.board_state import BoardState


class BoardHandler(BaseHTTPRequestHandler):
    """GET reads the page and the cards; POST runs a tool call. A subclass binds `state`."""

    state: ClassVar[BoardState]
    timeout: ClassVar[float | None] = 30  # seconds a connection may stall before it is dropped
    server_version = "tadu"
    sys_version = ""

    @override
    def parse_request(self) -> bool:
        """Refuse every method but GET and POST before it is dispatched."""
        parsed = super().parse_request()
        if not parsed or self.allows():
            return parsed
        refusal = json_error(HTTPStatus.METHOD_NOT_ALLOWED, "only GET and POST")
        send_board_response(self, refusal, ("Allow", "GET, POST"))
        return False

    def allows(self) -> bool:
        """Whether the request's method may be dispatched: GET and POST."""
        return self.command in ("GET", "POST")

    def do_GET(self) -> None:
        """Check Host, and the token on the cards, then serve the page, an asset or the cards."""
        route = self.path.partition("?")[0]
        token = request_token(self.path, self.headers.get("X-Tadu-Token"))
        refusal = authorize_request(self.headers.get("Host"), token, route, self.state)
        if refusal is not None:
            send_board_response(self, json_error(refusal, HTTPStatus(refusal).phrase.lower()))
            return
        today = datetime.now(UTC).astimezone().date()
        send_board_response(self, board_route(self.path, self.state, today))

    def do_POST(self) -> None:
        """Check the call comes from the board's page (see authorize_post), then run it."""
        refusal = authorize_post(self.headers, self.state)
        if refusal is not None:
            send_board_response(self, json_error(*refusal))
            return
        body = self.rfile.read(int(self.headers["Content-Length"]))
        send_board_response(self, board_call(self.path, body, self.state))

    @override
    def end_headers(self) -> None:
        """Add the security headers to every response, errors included."""
        for name, value in BOARD_HEADERS.items():
            self.send_header(name, value)
        super().end_headers()

    @override
    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        """Log through log_message with the status only; a passed check of the page, none.

        Every open page checks once a minute; only the checks that fail say something.
        """
        if code == HTTPStatus.OK and self.path.partition("?")[0].endswith(BOARD_CHECK_PATH):
            return
        self.log_message("%s", code)

    @override
    def log_error(self, format: str, *args: object) -> None:
        """Drop: the base messages can quote the raw request line, token included."""

    @override
    def log_message(self, format: str, *args: object) -> None:
        """Write method, path without its query string, and status to the process's stderr.

        Not `sys.stderr`: while a tool call runs, that is its captured errors. Characters that
        are not printable are written escaped, so a request cannot send terminal control
        sequences, or a line break, into the operator's log.
        """
        path = getattr(self, "path", "").partition("?")[0]
        line = f"{self.command} {path} {format % args}"
        escaped = "".join(c if c.isprintable() else f"\\x{ord(c):02x}" for c in line)
        (sys.__stderr__ or sys.stderr).write(escaped + "\n")
