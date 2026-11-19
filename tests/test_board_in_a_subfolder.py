"""A team board at https://mydomain.com/tadu, behind a proxy that keeps the subfolder in
the paths it forwards (`/tadu/api/cards`) or takes it away (`/api/cards`).
"""

import json
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from board_server import BoardServer
from fake_github import FakeGithub, fake_github
from team_board import call, cookies, serve_team_board, sign_in_as, state_part
from team_workspace import team_workspace

from tadu.sign_in_limit import sign_in_limit
from tadu.sign_in_limiter import SignInLimiter

URL = "https://mydomain.com/tadu"
KEPT, TAKEN = "/tadu", ""


@pytest.fixture
def github() -> Iterator[FakeGithub]:
    with fake_github({"ana": {"acme/shop"}, "bo": {"acme/shop", "acme/vault"}}) as fake:
        yield fake


@pytest.fixture
def board_url() -> str:
    return URL


def titles(board: BoardServer, path: str, cookie: str) -> list[str]:
    response = call(board, "GET", path, cookie)
    assert response.status == 200, response.body
    return [card["title"] for card in json.loads(response.body)["cards"]]


@pytest.mark.parametrize("prefix", [KEPT, TAKEN])
def test_signing_in_comes_back_to_the_subfolder(
    board: BoardServer, github: FakeGithub, prefix: str
) -> None:
    assert board.host == "mydomain.com"
    start = call(board, "GET", f"{prefix}/auth/login")
    assert start.status == 302
    query = {k: v[0] for k, v in parse_qs(urlsplit(start.headers["Location"]).query).items()}
    assert query["redirect_uri"] == "https://mydomain.com/tadu/auth/callback"
    kept = cookies(start)["__Secure-tadu_oauth_state"]
    assert state_part(kept) == query["state"]
    assert start.headers["Set-Cookie"] == (
        f"__Secure-tadu_oauth_state={kept}; Path=/tadu/; Max-Age=600; "
        "HttpOnly; SameSite=Lax; Secure"
    )
    back = call(
        board,
        "GET",
        f"{prefix}/auth/callback?code=code-ana&state={query['state']}",
        f"__Secure-tadu_oauth_state={kept}",
    )
    assert back.status == 302, back.body
    assert back.headers["Location"] == "/tadu/"
    headers = back.headers.get_all("Set-Cookie", [])
    session = next(h for h in headers if h.startswith("__Secure-tadu_session="))
    assert "; Path=/tadu/; " in session
    assert session.endswith("; HttpOnly; SameSite=Lax; Secure")
    assert not any(h.startswith("__Host-") or "Path=/;" in h for h in headers)
    assert github.redirect_uris == ["https://mydomain.com/tadu/auth/callback"]
    cookie = "__Secure-tadu_session=" + cookies(back)["__Secure-tadu_session"]
    assert titles(board, f"{prefix}/api/cards", cookie) == ["shop item."]


@pytest.mark.parametrize("prefix", [KEPT, TAKEN])
def test_the_page_and_its_relative_links_work_from_the_subfolder(
    board: BoardServer, prefix: str
) -> None:
    signed_out = call(board, "GET", f"{prefix}/")
    assert signed_out.status == 200
    assert b'href="auth/login"' in signed_out.body
    assert b'href="board.css"' in signed_out.body
    ana = sign_in_as(board, "ana", prefix)
    page = call(board, "GET", f"{prefix}/", ana)
    assert b'src="app.js"' in page.body
    for asset in ("app.js", "board.css", "fetch-cards.js", "sign-out.js"):
        assert call(board, "GET", f"{prefix}/{asset}").status == 200, asset
    assert call(board, "GET", f"{prefix}/nope.js").status == 404


def test_either_proxy_style_reaches_the_same_session(board: BoardServer) -> None:
    bo = sign_in_as(board, "bo", KEPT)
    assert bo.startswith("__Secure-tadu_session=")
    assert titles(board, "/tadu/api/cards", bo) == ["shop item.", "vault item."]
    assert titles(board, "/api/cards", bo) == ["shop item.", "vault item."]
    signed_out = call(board, "POST", "/tadu/auth/logout", bo)
    assert signed_out.status == 200
    assert signed_out.headers["Set-Cookie"].startswith("__Secure-tadu_session=; Path=/tadu/;")
    assert call(board, "GET", "/api/cards", bo).status == 401
    assert call(board, "GET", "/tadu/api/cards", bo).status == 401


@pytest.mark.parametrize(
    ("path", "location"), [("/tadu", "/tadu/"), ("/tadu?token=x", "/tadu/?token=x")]
)
def test_the_subfolder_without_its_slash_moves_to_it(
    board: BoardServer, path: str, location: str
) -> None:
    moved = call(board, "GET", path)
    assert moved.status == 308
    assert moved.headers["Location"] == location
    assert "Set-Cookie" not in moved.headers


def test_only_the_public_host_is_answered(board: BoardServer) -> None:
    for host in ("evil.example", "mydomain.com.evil.example", "tadu.mydomain.com"):
        answer = board.request("GET", "/tadu", {"Host": host})
        assert answer.status == 421, host
        assert board.request("GET", "/tadu/", {"Host": host}).status == 421, host


def test_a_root_session_cookie_is_not_the_boards(board: BoardServer) -> None:
    bo = sign_in_as(board, "bo", KEPT)
    value = bo.partition("=")[2]
    # Another app of mydomain.com cannot make the board take a __Host- or plain cookie.
    for name in ("__Host-tadu_session", "tadu_session"):
        assert call(board, "GET", "/tadu/api/cards", f"{name}={value}").status == 401


def test_sign_out_is_the_only_post(board: BoardServer) -> None:
    for path in ("/tadu", "/tadu/", "/tadu/api/cards", "/tadu/auth/login", "/tadu/auth/logoutx"):
        assert call(board, "POST", path).status == 405, path


def test_sign_in_limits_count_both_proxy_styles_together(
    tmp_path: Path, github: FakeGithub
) -> None:
    limiter = SignInLimiter(sign_in_limit("4/minute"))
    with serve_team_board(team_workspace(tmp_path), github, URL, limiter=limiter) as board:
        paths = ["/tadu/auth/login", "/auth/login"] * 2
        assert [call(board, "GET", p).status for p in paths] == [302] * 4
        assert call(board, "GET", "/tadu/auth/login").status == 429
        assert call(board, "GET", "/auth/login").status == 429
        assert call(board, "GET", "/tadu/").status == 200


@pytest.mark.parametrize("url", ["https://tadu.mydomain.com", "https://mytadudomain.com"])
def test_a_board_of_its_own_host_keeps_to_the_root(
    tmp_path: Path, github: FakeGithub, url: str
) -> None:
    with serve_team_board(team_workspace(tmp_path), github, url) as board:
        assert board.host == url.removeprefix("https://")
        start = call(board, "GET", "/auth/login")
        query = parse_qs(urlsplit(start.headers["Location"]).query)
        assert query["redirect_uri"] == [f"{url}/auth/callback"]
        assert start.headers["Set-Cookie"].startswith("__Host-tadu_oauth_state=")
        assert "; Path=/; " in start.headers["Set-Cookie"]
        ana = sign_in_as(board, "ana")
        assert ana.startswith("__Host-tadu_session=")
        assert titles(board, "/api/cards", ana) == ["shop item."]
        assert call(board, "GET", "/tadu").status == 404
        assert board.request("GET", "/", {"Host": "mydomain.com"}).status == 421
