import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from board_server import BoardServer, get, send, serve_board, with_cookie
from board_workspace import board_workspace

from tadu.board_headers import BOARD_HEADERS


@pytest.fixture
def board(tmp_path: Path) -> Iterator[BoardServer]:
    with serve_board(board_workspace(tmp_path)) as server:
        yield server


def no_cors(response_headers: object) -> bool:
    return not any(h.lower().startswith("access-control") for h in response_headers)  # type: ignore[attr-defined]


def test_wrong_host_and_wrong_token_are_refused(board: BoardServer) -> None:
    assert get(board, "/api/cards", host="evil.example:80", token=board.token).status == 421
    assert get(board, "/api/cards", host=None, token=board.token).status == 421
    assert get(board, "/api/cards", host=board.host, token="nope").status == 403  # noqa: S106
    assert get(board, "/api/cards", host=board.host, token=None).status == 403
    assert get(board, "/", host=board.host, token="t%C3%A9").status == 403  # noqa: S106


def test_cards_json_and_security_headers(board: BoardServer) -> None:
    response = get(board, "/api/cards", host=board.host, token=board.token)
    assert response.status == 200
    assert response.headers["Content-Type"] == "application/json; charset=utf-8"
    assert json.loads(response.body)["cards"][0]["title"] == "<script>alert(1)</script>"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert no_cors(response.headers)
    assert "Set-Cookie" not in response.headers


def test_errors_carry_the_headers_too(board: BoardServer) -> None:
    for response in (
        get(board, "/", host="evil.example:80", token=None),
        get(board, "/", host=board.host, token=None),
        get(board, "/nope", host=board.host, token=board.token),
        send(board, "POST", "/"),
    ):
        for name, value in BOARD_HEADERS.items():
            assert response.headers[name] == value
        assert no_cors(response.headers)
        assert "Set-Cookie" not in response.headers


def test_cookie_set_on_index_then_accepted(board: BoardServer) -> None:
    index = get(board, "/?view=all", host=board.host, token=board.token)
    assert index.status == 200
    assert index.headers["Content-Type"] == "text/html; charset=utf-8"
    cookie = index.headers["Set-Cookie"]
    assert cookie == f"tadu_board={board.token}; HttpOnly; SameSite=Strict; Path=/"
    pair = cookie.split(";")[0]
    assert with_cookie(board, "/api/cards", pair).status == 200
    assert with_cookie(board, "/board.js", pair).status == 200
    bad = with_cookie(board, "/api/cards", "tadu_board=nope")
    assert bad.status == 403
    asset = get(board, "/board.css", host=board.host, token=board.token)
    assert "Set-Cookie" not in asset.headers


def test_methods_and_unknown_paths(board: BoardServer) -> None:
    for method in ("POST", "HEAD", "PUT", "DELETE", "OPTIONS", "BREW"):
        response = send(board, method, "/")
        assert response.status == 405
        assert response.headers["Allow"] == "GET"
    assert get(board, "/nope", host=board.host, token=board.token).status == 404
    assert get(board, "/nope", host=board.host, token=None).status == 403


def test_workspace_broken_mid_run_is_500(board: BoardServer) -> None:
    (board.state.workspace / "tadu-workspace.toml").write_text("version = ")
    response = get(board, "/api/cards", host=board.host, token=board.token)
    assert response.status == 500
    assert "error" in json.loads(response.body)


def test_log_omits_the_query(board: BoardServer, capfd: pytest.CaptureFixture[str]) -> None:
    get(board, "/api/cards?x=1", host=board.host, token=board.token)
    send(board, "POST", "/")
    err = capfd.readouterr().err
    assert "GET /api/cards 200" in err
    assert "POST / 405" in err
    assert board.token not in err
