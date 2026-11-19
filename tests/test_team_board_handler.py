import json
import time
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from board_server import BoardServer, Response
from fake_github import FakeGithub, fake_github, pkce_challenge
from team_board import call, cookies, serve_team_board, sign_in_as, state_part
from team_workspace import team_workspace

from tadu.board_headers import BOARD_HEADERS
from tadu.token_grant import TokenGrant


@pytest.fixture
def github() -> Iterator[FakeGithub]:
    with fake_github({"Ana-Dev": {"acme/shop"}, "bo": {"acme/shop", "acme/vault"}}) as fake:
        yield fake


@pytest.fixture
def board(tmp_path: Path, github: FakeGithub) -> Iterator[BoardServer]:
    with serve_team_board(team_workspace(tmp_path), github) as server:
        yield server


def check_headers(response: Response) -> None:
    for name, value in BOARD_HEADERS.items():
        assert response.headers[name] == value
    assert not any(h.lower().startswith("access-control") for h in response.headers)


def titles(response: Response) -> list[str]:
    assert response.status == 200
    return [card["title"] for card in json.loads(response.body)["cards"]]


def test_signed_out_sees_the_sign_in_page_and_no_cards(board: BoardServer) -> None:
    page = call(board, "GET", "/")
    assert page.status == 200
    assert b'href="auth/login"' in page.body
    assert b"app.js" not in page.body
    assert call(board, "GET", "/app.js").status == 200
    refused = call(board, "GET", "/api/cards")
    assert refused.status == 401
    assert cookies(refused) == {"tadu_session": ""}
    assert call(board, "GET", f"/api/cards?token={board.token}").status == 401
    assert call(board, "GET", "/api/cards", "tadu_session=forged").status == 401
    for response in (page, refused):
        check_headers(response)


def test_sign_in_redirects_to_github_with_state(board: BoardServer, github: FakeGithub) -> None:
    start = call(board, "GET", "/auth/login")
    assert start.status == 302
    location = urlsplit(start.headers["Location"])
    assert f"{location.scheme}://{location.netloc}{location.path}" == (
        f"{github.url}/login/oauth/authorize"
    )
    query = {k: v[0] for k, v in parse_qs(location.query).items()}
    assert query["client_id"] == "client-1"
    assert query["redirect_uri"] == f"http://{board.host}/auth/callback"
    assert query["scope"] == "repo"
    kept = cookies(start)["tadu_oauth_state"]
    assert state_part(kept) == query["state"]
    verifier = kept.partition(".")[2]
    assert len(verifier) == 64
    assert query["code_challenge"] == pkce_challenge(verifier)
    assert query["code_challenge_method"] == "S256"
    assert (query["prompt"], query["allow_signup"]) == ("select_account", "false")
    header = start.headers["Set-Cookie"]
    assert "HttpOnly" in header
    assert "SameSite=Lax" in header
    assert "Secure" not in header
    check_headers(start)


def test_each_person_sees_only_what_they_read(board: BoardServer) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    bo = sign_in_as(board, "bo")
    assert titles(call(board, "GET", "/api/cards", ana)) == ["shop item."]
    assert titles(call(board, "GET", "/api/cards", bo)) == ["shop item.", "vault item."]
    payload = json.loads(call(board, "GET", "/api/cards", ana).body)
    assert (payload["user"], payload["me"]) == ("Ana-Dev", "ana")
    page = call(board, "GET", "/", ana)
    assert b'src="app.js"' in page.body


def test_the_callback_sets_a_session_cookie_and_forgets_the_state(board: BoardServer) -> None:
    start = call(board, "GET", "/auth/login")
    state = cookies(start)["tadu_oauth_state"]
    back = call(
        board,
        "GET",
        f"/auth/callback?code=code-bo&state={state_part(state)}",
        f"tadu_oauth_state={state}",
    )
    assert back.headers["Location"] == "/"
    set_cookies = back.headers.get_all("Set-Cookie", [])
    assert set_cookies[0].startswith("tadu_session=")
    assert "Max-Age=1209600; HttpOnly; SameSite=Lax" in set_cookies[0]
    assert set_cookies[1].startswith("tadu_oauth_state=; Path=/; Max-Age=0")


@pytest.mark.parametrize(
    ("query", "cookie", "status"),
    [
        ("code=code-bo&state=s1", "tadu_oauth_state=s2.v", 400),
        ("code=code-bo&state=s1", "", 400),
        ("code=code-bo&state=s1", "tadu_oauth_state=s1", 400),  # no PKCE verifier
        ("code=code-bo&state=s1", "tadu_oauth_state=s1.", 400),
        ("code=code-bo&state=s1.v", "tadu_oauth_state=s1.v", 400),
        ("code=code-bo", "tadu_oauth_state=s1.v", 400),
        ("error=access_denied&state=s1", "tadu_oauth_state=s1.v", 403),
        ("code=stale&state=s1", "tadu_oauth_state=s1.v", 502),
        ("code=code-revoked&state=s1", "tadu_oauth_state=s1.v", 502),
    ],
)
def test_a_failed_callback_starts_no_session(
    board: BoardServer, query: str, cookie: str, status: int
) -> None:
    back = call(board, "GET", f"/auth/callback?{query}", cookie)
    assert back.status == status
    assert back.headers["Content-Type"] == "text/plain; charset=utf-8"
    assert back.body.startswith(b"Sign-in failed: ")
    # No session; the sign-in cookie is spent, whatever went wrong.
    spent = back.headers.get_all("Set-Cookie", [])
    assert len(spent) == 1
    assert spent[0].startswith("tadu_oauth_state=; Path=/; Max-Age=0")
    check_headers(back)


def test_sign_out_ends_the_session(board: BoardServer) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    out = call(board, "POST", "/auth/logout", ana)
    assert out.status == 200
    assert cookies(out) == {"tadu_session": ""}
    assert "Max-Age=0" in out.headers["Set-Cookie"]
    check_headers(out)
    assert call(board, "GET", "/api/cards", ana).status == 401
    assert b'href="auth/login"' in call(board, "GET", "/", ana).body
    assert call(board, "POST", "/auth/logout").status == 200


def test_a_token_revoked_on_github_ends_the_session(board: BoardServer) -> None:
    assert board.state.github is not None
    sessions = board.state.github.sessions
    value = sessions.create("Ana-Dev", TokenGrant("tok-revoked"), time.time())
    refused = call(board, "GET", "/api/cards", f"tadu_session={value}")
    assert refused.status == 401
    assert cookies(refused) == {"tadu_session": ""}
    assert sessions.find(value, time.time()) is None


def test_other_methods_and_hosts_are_refused(board: BoardServer) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    for method, path in (("POST", "/api/cards"), ("PUT", "/auth/logout"), ("DELETE", "/")):
        response = call(board, method, path, ana)
        assert response.status == 405
        assert response.headers["Allow"] == "GET, POST"
    for method, path in (("GET", "/api/cards"), ("GET", "/auth/login"), ("POST", "/auth/logout")):
        misdirected = board.request(method, path, {"Host": "evil.example:80", "Cookie": ana})
        assert misdirected.status == 421
        check_headers(misdirected)
    assert titles(call(board, "GET", "/api/cards", ana)) == ["shop item."]
    assert call(board, "GET", "/nope", ana).status == 404


def test_log_omits_the_code_and_session(
    board: BoardServer, capfd: pytest.CaptureFixture[str]
) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    call(board, "GET", "/api/cards", ana)
    err = capfd.readouterr().err
    assert "GET /auth/callback 302" in err
    assert "code-" not in err
    assert ana.partition("=")[2] not in err
