import http.client
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from tadu.allowed_hosts import allowed_hosts
from tadu.board_state import BoardState
from tadu.make_board_handler import make_board_handler

TOKEN = "test-token"  # noqa: S105


@dataclass(frozen=True)
class Response:
    status: int
    headers: http.client.HTTPMessage
    body: bytes


@dataclass(frozen=True)
class BoardServer:
    host: str
    token: str
    state: BoardState

    def request(self, method: str, path: str, headers: dict[str, str]) -> Response:
        port = int(self.host.rpartition(":")[2])
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        try:
            connection.putrequest(method, path, skip_host=True, skip_accept_encoding=True)
            for name, value in headers.items():
                connection.putheader(name, value)
            connection.endheaders()
            reply = connection.getresponse()
            return Response(reply.status, reply.headers, reply.read())
        finally:
            connection.close()


@contextmanager
def serve_board(workspace: Path) -> Iterator[BoardServer]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), BaseHTTPRequestHandler)
    port = server.server_address[1]
    state = BoardState(workspace, 14, TOKEN, allowed_hosts("127.0.0.1", port))
    server.RequestHandlerClass = make_board_handler(state)
    thread = threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True)
    thread.start()
    try:
        yield BoardServer(f"127.0.0.1:{port}", TOKEN, state)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def get(
    board: BoardServer,
    path: str,
    *,
    host: str | None,
    token: str | None,
) -> Response:
    headers = {} if host is None else {"Host": host}
    query = "" if token is None else ("&" if "?" in path else "?") + f"token={token}"
    return board.request("GET", path + query, headers)


def send(board: BoardServer, method: str, path: str) -> Response:
    return board.request(method, f"{path}?token={board.token}", {"Host": board.host})


def with_cookie(board: BoardServer, path: str, cookie: str) -> Response:
    return board.request("GET", path, {"Host": board.host, "Cookie": cookie})
