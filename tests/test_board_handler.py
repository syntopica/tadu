import json
import socket
from collections.abc import Iterator
from pathlib import Path

import pytest
from board_server import BoardServer, get, send, serve_board, with_header
from board_workspace import board_workspace
from check_board_headers import check_board_headers
from response import Response

from tadu.board_handler import BoardHandler

ASSETS = ("/", "/app.js", "/card-visible.js", "/board.css")


@pytest.fixture
def board(tmp_path: Path) -> Iterator[BoardServer]:
    with serve_board(board_workspace(tmp_path)) as server:
        yield server


def check_headers(response: Response) -> None:
    check_board_headers(response)
    assert "Set-Cookie" not in response.headers


def test_assets_need_only_the_host(board: BoardServer) -> None:
    for path in ASSETS:
        response = get(board, path, host=board.host, token=None)
        assert response.status == 200
        check_headers(response)
        assert get(board, path, host="evil.example:80", token=None).status == 421
        assert get(board, path, host=None, token=None).status == 421
    page = get(board, "/", host=board.host, token=None)
    assert page.headers["Content-Type"] == "text/html; charset=utf-8"


def test_wrong_host_and_wrong_token_are_refused(board: BoardServer) -> None:
    assert get(board, "/api/cards", host="evil.example:80", token=board.token).status == 421
    assert get(board, "/api/cards", host=None, token=board.token).status == 421
    assert get(board, "/api/cards", host=board.host, token="nope").status == 403  # noqa: S106
    assert get(board, "/api/cards", host=board.host, token=None).status == 403
    assert get(board, "/api/cards", host=board.host, token="t%C3%A9").status == 403  # noqa: S106
    assert with_header(board, "/api/cards", "nope").status == 403


def test_cards_by_query_token_and_by_header(board: BoardServer) -> None:
    for response in (
        get(board, "/api/cards", host=board.host, token=board.token),
        with_header(board, "/api/cards", board.token),
    ):
        assert response.status == 200
        assert response.headers["Content-Type"] == "application/json; charset=utf-8"
        assert json.loads(response.body)["cards"][0]["title"] == "<script>alert(1)</script>"
        assert response.headers["Referrer-Policy"] == "same-origin"
        check_headers(response)


def test_errors_carry_the_headers_too(board: BoardServer) -> None:
    for response in (
        get(board, "/", host="evil.example:80", token=None),
        get(board, "/api/cards", host=board.host, token=None),
        get(board, "/nope", host=board.host, token=board.token),
        send(board, "POST", "/"),
    ):
        check_headers(response)


def test_methods_and_unknown_paths(board: BoardServer) -> None:
    for method in ("HEAD", "PUT", "DELETE", "OPTIONS", "BREW"):
        response = send(board, method, "/api/cards")
        assert response.status == 405
        assert response.headers["Allow"] == "GET, POST"
        check_headers(response)
    assert get(board, "/nope", host=board.host, token=None).status == 404
    assert get(board, "/nope", host="evil.example:80", token=None).status == 421


def test_workspace_broken_mid_run_is_500(board: BoardServer) -> None:
    (board.state.workspace / "tadu-workspace.toml").write_text("version = ")
    response = get(board, "/api/cards", host=board.host, token=board.token)
    assert response.status == 500
    assert "error" in json.loads(response.body)


def test_log_omits_the_query(board: BoardServer, capfd: pytest.CaptureFixture[str]) -> None:
    get(board, "/api/cards?x=1", host=board.host, token=board.token)
    with_header(board, "/api/cards", board.token)
    send(board, "PUT", "/")
    port = int(board.host.rpartition(":")[2])
    with socket.create_connection(("127.0.0.1", port), timeout=5) as raw:
        raw.sendall(f"GET /?token={board.token} HTTP/9 junk\r\n\r\n".encode())
        answer = b"".join(iter(lambda: raw.recv(4096), b""))
    # Python 3.12.3 answers a bad request line as HTTP/0.9, without a status line;
    # later releases send `HTTP/1.0 400`. Either way it is the 400 error, never the page.
    assert answer.startswith(b"HTTP/1.0 400") or b"Error code: 400" in answer
    assert b'src="app.js"' not in answer
    err = capfd.readouterr().err
    assert "GET /api/cards 200" in err
    assert "PUT / 405" in err
    assert board.token not in err


def test_a_stalled_connection_is_dropped() -> None:
    assert BoardHandler.timeout == 30
