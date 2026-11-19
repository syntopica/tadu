"""No request of tadu's ever reaches a host other than the one it was sent to.

GitHub answers with redirects (a renamed repository), and tadu follows those on GitHub's
own origin. A redirect anywhere else is not followed: the other host is not contacted at
all, with or without a token, and a token request never sends its client secret or
refresh token on. `elsewhere` is a second server that records every request it gets.
"""

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
import requests
from fake_github import FakeGithub, fake_github
from team_board import call, serve_team_board, sign_in_as
from team_workspace import team_workspace

from tadu.exchange_github_code import exchange_github_code
from tadu.github_call import github_call
from tadu.github_reply import GithubReply
from tadu.refresh_github_token import refresh_github_token
from tadu.repository_status import repository_status
from tadu.same_origin_redirects import SameOriginRedirects
from tadu.token_access import TokenAccess

REDIRECTS = (301, 302, 303, 307, 308)


@pytest.fixture
def github() -> Iterator[FakeGithub]:
    with fake_github({"ana": {"acme/shop", "acme/shop-v2"}}) as fake:
        yield fake


@pytest.fixture
def elsewhere() -> Iterator[FakeGithub]:
    with fake_github({"ana": {"acme/shop"}}) as fake:
        yield fake


def shop(github: FakeGithub) -> str:
    return f"{github.url}/api/repos/acme/shop"


@pytest.mark.parametrize("status", REDIRECTS)
def test_an_api_redirect_to_another_host_is_not_followed(
    github: FakeGithub, elsewhere: FakeGithub, status: int
) -> None:
    github.moved_status = status
    github.moved["acme/shop"] = f"{elsewhere.url}/api/repos/acme/shop"
    assert github_call(shop(github), "tok-ana").status == status
    assert elsewhere.requests == []


@pytest.mark.parametrize(
    "location",
    [
        "{elsewhere}/api/repos/acme/shop",
        "//{elsewhere_host}/api/repos/acme/shop",
        "https://{github_host}/api/repos/acme/shop",
        "http://{github_host}@{elsewhere_host}/api/repos/acme/shop",
        "http://user:pass@{elsewhere_host}/api/repos/acme/shop",
        "http://localhost:{elsewhere_port}/api/repos/acme/shop",
        "HTTP://{elsewhere_host}/api/repos/acme/shop",
        "http://{github_host}:99999/api/repos/acme/shop",
        "ftp://{github_host}/api/repos/acme/shop",
    ],
)
def test_no_form_of_location_leads_elsewhere(
    github: FakeGithub, elsewhere: FakeGithub, location: str
) -> None:
    github.moved["acme/shop"] = location.format(
        elsewhere=elsewhere.url,
        elsewhere_host=elsewhere.url.removeprefix("http://"),
        elsewhere_port=elsewhere.url.rpartition(":")[2],
        github_host=github.url.removeprefix("http://"),
    )
    assert github_call(shop(github), "tok-ana").status == 301
    assert elsewhere.requests == []
    assert github.requests == ["GET /api/repos/acme/shop"]


def test_a_rename_on_the_same_host_is_followed_then_stopped_at_the_border(
    github: FakeGithub, elsewhere: FakeGithub
) -> None:
    github.renamed["acme/shop"] = "acme/shop-v2"
    followed = repository_status(github.sign_in(), "tok-ana", "acme/shop", TokenAccess())
    assert followed == (200, github.repo_id("acme/shop-v2"), "acme/shop-v2")
    github.moved["acme/shop-v2"] = f"{elsewhere.url}/api/repos/acme/shop"
    chained = github_call(shop(github), "tok-ana")
    assert chained.status == 301
    assert elsewhere.requests == []


@pytest.mark.parametrize("status", REDIRECTS)
def test_a_token_request_never_carries_the_secret_elsewhere(
    github: FakeGithub, elsewhere: FakeGithub, status: int
) -> None:
    sign_in = github.sign_in()
    grant = exchange_github_code(sign_in, "code-ana", "verifier")
    assert grant is not None
    assert grant.refresh_token is not None
    github.token_moved = f"{elsewhere.url}/login/oauth/access_token"
    github.token_moved_status = status
    assert exchange_github_code(sign_in, "code-ana~again", "verifier") is None
    assert refresh_github_token(sign_in, grant.refresh_token) is None
    assert elsewhere.requests == []


@pytest.fixture
def netrc_for_every_host(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An operator's ~/.netrc with a password for the host both servers run on."""
    netrc = tmp_path / ".netrc"
    netrc.write_text("machine 127.0.0.1 login operator password hunter2\n")
    netrc.chmod(0o600)
    monkeypatch.setenv("NETRC", str(netrc))


@pytest.mark.usefixtures("netrc_for_every_host")
def test_a_netrc_never_answers_for_a_persons_token(
    github: FakeGithub, elsewhere: FakeGithub
) -> None:
    assert github_call(shop(github), "tok-ana").status == 200
    github.renamed["acme/shop"] = "acme/shop-v2"
    renamed = repository_status(github.sign_in(), "tok-ana", "acme/shop", TokenAccess())
    assert renamed[0] == 200
    assert github.authorizations == ["Bearer tok-ana"] * 3
    github.moved["acme/shop-v2"] = f"{elsewhere.url}/api/repos/acme/shop"
    assert github_call(shop(github), "tok-ana").status == 301
    assert elsewhere.requests == []


@pytest.mark.usefixtures("netrc_for_every_host")
def test_a_netrc_never_answers_for_the_app_either(github: FakeGithub) -> None:
    sign_in = github.sign_in()
    grant = exchange_github_code(sign_in, "code-ana", "verifier")
    assert grant is not None
    assert grant.refresh_token is not None
    assert refresh_github_token(sign_in, grant.refresh_token) is not None
    assert github.authorizations == ["", ""]


def test_the_board_hides_a_repository_that_redirects_away(
    tmp_path: Path, elsewhere: FakeGithub
) -> None:
    with fake_github({"Ana-Dev": set()}, public=frozenset({"acme/shop", "acme/vault"})) as github:
        github.moved["acme/vault"] = f"{elsewhere.url}/api/repos/acme/vault"
        with serve_team_board(team_workspace(tmp_path), github) as board:
            body = json.loads(call(board, "GET", "/api/cards", sign_in_as(board, "Ana-Dev")).body)
    assert [card["repository"] for card in body["cards"]] == ["shop"]
    assert [p["message"] for p in body["problems"]] == [
        "GitHub answered HTTP 301, so some repositories are hidden until Reload can check them"
    ]
    assert elsewhere.requests == []


@pytest.mark.parametrize(
    ("url", "origin"),
    [
        ("https://api.github.com/x", ("https", "api.github.com", 443)),
        ("https://API.GitHub.com:443/x", ("https", "api.github.com", 443)),
        ("http://127.0.0.1:8123/x", ("http", "127.0.0.1", 8123)),
        ("https://api.github.com:99999/x", None),
        ("ftp://host/x", None),
        ("/relative", None),
    ],
)
def test_origin(url: str, origin: tuple[str, str, int] | None) -> None:
    assert SameOriginRedirects.origin(url) == origin


def test_if_the_redirect_guard_ever_failed_the_answer_from_elsewhere_is_still_not_read(
    github: FakeGithub, elsewhere: FakeGithub, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        SameOriginRedirects, "get_redirect_target", requests.Session.get_redirect_target
    )
    github.moved["acme/shop"] = f"{elsewhere.url}/api/repos/acme/shop"
    reply = github_call(shop(github), "tok-ana")
    assert reply == GithubReply(301)
    assert elsewhere.authorizations == [""]
