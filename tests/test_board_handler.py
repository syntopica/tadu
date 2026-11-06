import json
import socket
from collections.abc import Iterator
from pathlib import Path

import pytest
from board_server import BoardServer, Response, get, send, serve_board, with_header
from board_workspace import board_workspace

from tadu.board_headers import BOARD_HEADERS

ASSETS = ("/", "/board.js", "/filters.js", "/board.css")


@pytest.fixture
def board(tmp_path: Path) -> Iterator[BoardServer]:
    with serve_board(board_workspace(tmp_path)) as server:
        yield server


def check_headers(response: Response) -> None:
    for name, value in BOARD_HEADERS.items():
        assert response.headers[name] == value
    assert not any(h.lower().startswith("access-control") for h in response.headers)
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
        assert response.headers["Referrer-Policy"] == "no-referrer"
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
    for method in ("POST", "HEAD", "PUT", "DELETE", "OPTIONS", "BREW"):
        response = send(board, method, "/api/cards")
        assert response.status == 405
        assert response.headers["Allow"] == "GET"
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
    send(board, "POST", "/")
    port = int(board.host.rpartition(":")[2])
    with socket.create_connection(("127.0.0.1", port), timeout=5) as raw:
        raw.sendall(f"GET /?token={board.token} HTTP/9 junk\r\n\r\n".encode())
        assert raw.recv(64).startswith(b"HTTP/1.0 400")
    err = capfd.readouterr().err
    assert "GET /api/cards 200" in err
    assert "POST / 405" in err
    assert board.token not in err
