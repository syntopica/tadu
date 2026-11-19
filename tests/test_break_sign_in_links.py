"""Sign-in links someone else crafted, and paths that try to reach the cards around it."""

import json
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from board_server import BoardServer
from fake_github import FakeGithub, fake_github, pkce_challenge
from team_board import call, cookies, serve_team_board, sign_in_as, state_part
from team_workspace import team_workspace

TOKEN_EXCHANGE = "POST /login/oauth/access_token"  # noqa: S105 - a request line


@pytest.fixture
def github() -> Iterator[FakeGithub]:
    with fake_github({"Ana-Dev": {"acme/shop"}, "mallory": set()}) as fake:
        yield fake


@pytest.fixture
def board(tmp_path: Path, github: FakeGithub) -> Iterator[BoardServer]:
    with serve_team_board(team_workspace(tmp_path), github) as server:
        yield server


def state_of(board: BoardServer) -> str:
    return cookies(call(board, "GET", "/auth/login"))["tadu_oauth_state"]


def test_sign_in_ignores_where_a_link_says_to_go(board: BoardServer) -> None:
    start = call(
        board, "GET", "/auth/login?redirect_uri=https://evil.example/cb&next=//evil.example"
    )
    location = start.headers["Location"]
    assert "evil" not in location
    query = parse_qs(urlsplit(location).query)
    assert query["redirect_uri"] == [f"http://{board.host}/auth/callback"]
    other_name = board.request("GET", "/auth/login", {"Host": f"localhost:{board.port}"})
    assert (
        f"redirect_uri=http%3A%2F%2F{board.host.replace(':', '%3A')}"
        in other_name.headers["Location"]
    )


def test_the_callback_only_ever_goes_home(board: BoardServer) -> None:
    state = state_of(board)
    back = call(
        board,
        "GET",
        f"/auth/callback?code=code-Ana-Dev&state={state_part(state)}&next=https://evil.example&redirect=//x",
        f"tadu_oauth_state={state}",
    )
    assert back.status == 302
    assert back.headers["Location"] == "/"


def test_an_attackers_code_cannot_sign_the_victim_in(
    board: BoardServer, github: FakeGithub
) -> None:
    attacker_state = state_of(board)
    link = f"/auth/callback?code=code-mallory&state={attacker_state}"
    without_state = call(board, "GET", link)
    victim_state = state_of(board)
    with_own_state = call(board, "GET", link, f"tadu_oauth_state={victim_state}")
    for response in (without_state, with_own_state):
        assert response.status == 400
        assert "tadu_session" not in str(response.headers.get_all("Set-Cookie", []))
    assert TOKEN_EXCHANGE not in github.requests


def test_a_replayed_callback_starts_no_second_session(board: BoardServer) -> None:
    state = state_of(board)
    link = f"/auth/callback?code=code-Ana-Dev~replay&state={state_part(state)}"
    first = call(board, "GET", link, f"tadu_oauth_state={state}")
    again = call(board, "GET", link, f"tadu_oauth_state={state}")
    assert first.status == 302
    assert again.status == 502
    assert "tadu_session" not in str(again.headers.get_all("Set-Cookie", []))


def test_repeated_parameters_do_not_slip_past_the_state(board: BoardServer) -> None:
    state = state_of(board)
    mixed = call(
        board,
        "GET",
        f"/auth/callback?state=forged&state={state_part(state)}&code=code-Ana-Dev",
        f"tadu_oauth_state={state}",
    )
    assert mixed.status == 400


def test_nothing_a_link_says_is_echoed(board: BoardServer) -> None:
    state = state_of(board)
    script = "%3Cscript%3Ealert(1)%3C%2Fscript%3E"
    for query in (
        f"error=access_denied&error_description={script}&state={state_part(state)}",
        f"code={script}&state={state_part(state)}",
        f"code=x&state={script}",
    ):
        answer = call(board, "GET", f"/auth/callback?{query}", f"tadu_oauth_state={state}")
        assert answer.headers["Content-Type"] == "text/plain; charset=utf-8"
        assert b"script" not in answer.body
        assert b"alert" not in answer.body


@pytest.mark.parametrize(
    "path",
    [
        "/api/cards/",
        "/./api/cards",
        "/api/./cards",
        "/x/../api/cards",
        "/API/CARDS",
        "/api/cards;x",
        "/api/%63ards",
        "/api/cards%00",
        "/api/cards/../cards",
        "/auth/callback/../../api/cards",
        "/index.html",
    ],
)
def test_no_other_path_reaches_the_cards(board: BoardServer, path: str) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    for cookie in ("", ana):
        response = call(board, "GET", path, cookie)
        assert response.status in {401, 404}, (path, cookie, response.status)
        assert b"shop item" not in response.body


def test_a_doubled_slash_is_the_same_path_and_the_same_rules(board: BoardServer) -> None:
    # http.server turns a leading "//" into "/" before tadu sees the path.
    assert call(board, "GET", "//api/cards").status == 401
    ana = sign_in_as(board, "Ana-Dev")
    assert json.loads(call(board, "GET", "//api/cards", ana).body)["user"] == "Ana-Dev"


def test_sign_in_paths_are_exact(board: BoardServer) -> None:
    for path in ("/auth/login/", "/AUTH/LOGIN", "/auth/callback/", "/auth//callback"):
        assert call(board, "GET", path).status == 404


def test_https_cookies_planted_without_the_prefix_are_ignored(
    tmp_path: Path, github: FakeGithub
) -> None:
    public = "https://board.example.com"
    with serve_team_board(team_workspace(tmp_path), github, public) as board:
        ana = sign_in_as(board, "Ana-Dev")
        name, _, value = ana.partition("=")
        assert name == "__Host-tadu_session"
        assert json.loads(call(board, "GET", "/api/cards", ana).body)["user"] == "Ana-Dev"
        assert call(board, "GET", "/api/cards", f"tadu_session={value}").status == 401
        start = call(board, "GET", "/auth/login")
        assert start.headers["Set-Cookie"].startswith("__Host-tadu_oauth_state=")
        assert "; Secure" in start.headers["Set-Cookie"]
        state = cookies(start)["__Host-tadu_oauth_state"]
        tossed = call(
            board,
            "GET",
            f"/auth/callback?code=code-mallory&state={state_part(state)}",
            f"tadu_oauth_state={state}",
        )
        assert tossed.status == 400
        assert TOKEN_EXCHANGE not in github.requests[-1:]
        out = call(board, "POST", "/auth/logout", ana)
        assert out.headers["Set-Cookie"].startswith("__Host-tadu_session=; Path=/; Max-Age=0")
        assert call(board, "GET", "/api/cards", ana).status == 401


def test_a_stolen_code_is_worthless_without_the_browsers_verifier(
    board: BoardServer, github: FakeGithub
) -> None:
    """PKCE: GitHub binds the code to the challenge of the browser that asked for it."""
    victim = cookies(call(board, "GET", "/auth/login"))["tadu_oauth_state"]
    code = "code-Ana-Dev~leaked"
    github.challenges[code] = pkce_challenge(victim.partition(".")[2])
    thief = state_of(board)  # the thief's own sign-in, with its own verifier
    stolen = call(
        board,
        "GET",
        f"/auth/callback?code={code}&state={state_part(thief)}",
        f"tadu_oauth_state={thief}",
    )
    assert stolen.status == 502
    own = call(
        board,
        "GET",
        f"/auth/callback?code={code}&state={state_part(victim)}",
        f"tadu_oauth_state={victim}",
    )
    assert own.status == 302
    assert github.verifiers[-2:] == [thief.partition(".")[2], victim.partition(".")[2]]
