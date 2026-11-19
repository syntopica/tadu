import socket
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import pytest
from board_server import serve_board
from board_workspace import board_workspace

from tadu.board_http_server import BoardHttpServer


def test_a_client_gone_away_is_not_a_traceback(capfd: pytest.CaptureFixture[str]) -> None:
    server = BoardHttpServer(("127.0.0.1", 0), BaseHTTPRequestHandler, bind_and_activate=False)
    try:
        raise ConnectionResetError(104, "Connection reset by peer")  # noqa: TRY301
    except ConnectionResetError:
        server.handle_error(None, ("127.0.0.1", 1))
    assert capfd.readouterr().err == ""
    try:
        msg = "a bug"
        raise ValueError(msg)  # noqa: TRY301
    except ValueError:
        server.handle_error(None, ("127.0.0.1", 1))
    assert "ValueError: a bug" in capfd.readouterr().err
    server.server_close()
    assert sys.exc_info() == (None, None, None)


def test_a_request_cannot_write_control_characters_into_the_log(
    tmp_path: Path, capfd: pytest.CaptureFixture[str]
) -> None:
    with serve_board(board_workspace(tmp_path)) as board:
        port = int(board.host.rpartition(":")[2])
        with socket.create_connection(("127.0.0.1", port), timeout=5) as raw:
            raw.sendall(b"GET /\x1b[2J\x07x HTTP/1.1\r\nHost: " + board.host.encode() + b"\r\n\r\n")
            raw.recv(100)
    err = capfd.readouterr().err
    assert "\x1b" not in err
    assert "\x07" not in err
    assert "GET /\\x1b[2J\\x07x 404" in err
