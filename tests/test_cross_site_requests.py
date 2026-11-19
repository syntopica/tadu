"""Another page of the same site (a sibling subdomain, another port) gets the session
cookie along, since SameSite=Lax only stops other sites: it still cannot load the
cards, report activity or sign someone out, for the board wants its own page asking.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from board_server import BoardServer, Response
from fake_github import fake_github
from team_board import call, serve_team_board, sign_in_as
from team_workspace import team_workspace

OWN = "https://tadu.example.com"


@pytest.fixture
def board(tmp_path: Path) -> Iterator[BoardServer]:
    with (
        fake_github({"Ana-Dev": {"acme/shop"}}) as github,
        serve_team_board(team_workspace(tmp_path), github, f"{OWN}/tadu") as server,
    ):
        yield server


def ask(board: BoardServer, method: str, path: str, headers: dict[str, str]) -> Response:
    return board.request(method, path, {"Host": "tadu.example.com"} | headers)


@pytest.mark.parametrize("site", ["same-site", "cross-site", "none"])
@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/tadu/api/cards"),
        ("GET", "/tadu/api/session"),
        ("POST", "/tadu/api/session"),
        ("POST", "/tadu/auth/logout"),
        ("GET", "/api/cards"),
    ],
)
def test_another_pages_request_is_refused(
    board: BoardServer, site: str, method: str, path: str
) -> None:
    ana = sign_in_as(board, "Ana-Dev", "/tadu")
    refused = ask(board, method, path, {"Cookie": ana, "Sec-Fetch-Site": site})
    assert refused.status == 403
    assert b"did not come from the board's page" in refused.body
    assert "Set-Cookie" not in refused.headers
    assert call(board, "GET", "/tadu/api/session", ana).status == 200  # still signed in


@pytest.mark.parametrize("origin", ["https://evil.example.com", "null", "https://example.com"])
def test_a_post_from_another_origin_is_refused(board: BoardServer, origin: str) -> None:
    ana = sign_in_as(board, "Ana-Dev", "/tadu")
    for path in ("/tadu/api/session", "/tadu/auth/logout"):
        assert ask(board, "POST", path, {"Cookie": ana, "Origin": origin}).status == 403
    assert call(board, "GET", "/tadu/api/session", ana).status == 200


def test_the_boards_own_page_is_let_through(board: BoardServer) -> None:
    ana = sign_in_as(board, "Ana-Dev", "/tadu")
    own = {"Cookie": ana, "Sec-Fetch-Site": "same-origin"}
    assert ask(board, "GET", "/tadu/api/cards", own).status == 200
    assert ask(board, "POST", "/tadu/api/session", own | {"Origin": OWN}).status == 200
    assert ask(board, "POST", "/tadu/auth/logout", own | {"Origin": OWN}).status == 200
    assert call(board, "GET", "/tadu/api/session", ana).status == 401


@pytest.mark.parametrize("site", ["cross-site", "same-site", "none"])
def test_pages_and_the_way_back_from_github_are_not_guarded(board: BoardServer, site: str) -> None:
    # A link to the board, and GitHub's redirect back, come from other sites by nature.
    for path in ("/tadu/", "/tadu/app.js", "/tadu/auth/login"):
        assert ask(board, "GET", path, {"Sec-Fetch-Site": site}).status in {200, 302}, path
    back = ask(board, "GET", "/tadu/auth/callback?code=c&state=s", {"Sec-Fetch-Site": site})
    assert back.status == 400  # refused for its missing state, not for where it came from


def test_behind_https_browsers_are_told_to_keep_to_it(
    board: BoardServer, tmp_path_factory: pytest.TempPathFactory
) -> None:
    page = ask(board, "GET", "/tadu/", {})
    assert page.headers["Strict-Transport-Security"] == "max-age=31536000"
    assert page.headers["Cross-Origin-Resource-Policy"] == "same-origin"
    with (
        fake_github({"Ana-Dev": {"acme/shop"}}) as github,
        serve_team_board(team_workspace(tmp_path_factory.mktemp("plain")), github) as plain,
    ):
        assert "Strict-Transport-Security" not in call(plain, "GET", "/").headers
