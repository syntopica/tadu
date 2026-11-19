import socket

import pytest
from fake_github import FakeGithub, fake_github

from tadu.conditional_get import conditional_get
from tadu.exchange_github_code import exchange_github_code
from tadu.github_call import github_call
from tadu.github_reply import GithubReply
from tadu.github_user_login import github_user_login
from tadu.refresh_github_token import refresh_github_token
from tadu.repository_status import repository_status
from tadu.signed_out_error import SignedOutError
from tadu.token_access import TokenAccess
from tadu.token_grant import TokenGrant


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def test_call_reads_json_and_the_headers() -> None:
    with fake_github({}) as github:
        user = github_call(f"{github.url}/api/user", "tok-ana")
        ana = {"login": "ana", "id": github.user_id("ana")}
        assert (user.status, user.body, user.links) == (200, ana, {})
        assert user.etag is not None
        assert github_call(f"{github.url}/api/user", "tok-nobody").body == []
        flaky = github_call(f"{github.url}/api/repos/acme/flaky", "tok-ana")
        assert (flaky.status, flaky.body) == (502, None)
        assert github_call(f"{github.url}/api/user", "nope").status == 401
        assert github.authorizations[0] == "Bearer tok-ana"


def test_call_sends_the_etag_and_gets_a_304() -> None:
    with fake_github({}) as github:
        first = github_call(f"{github.url}/api/user", "tok-ana")
        again = github_call(f"{github.url}/api/user", "tok-ana", etag=first.etag)
        assert (again.status, again.body) == (304, None)
        assert github.not_modified == 1
        assert github_call(f"{github.url}/api/user", "tok-bo", etag=first.etag).status == 200


def test_call_to_an_unreachable_github_is_status_zero() -> None:
    assert github_call(f"http://127.0.0.1:{free_port()}/api/user", "t") == GithubReply(0)


def test_an_answer_that_breaks_off_is_status_zero() -> None:
    with fake_github({}) as github:
        assert github_call(f"{github.url}/api/repos/acme/truncated", "tok-ana") == GithubReply(0)


def test_conditional_get_remembers_what_it_read() -> None:
    with fake_github({}) as github:
        url = f"{github.url}/api/user"
        memo: dict[str, tuple[str, str]] = {}
        reads: list[int] = []

        def read(reply: GithubReply) -> str:
            reads.append(reply.status)
            return str(reply.body)

        ana = str({"login": "ana", "id": github.user_id("ana")})
        assert conditional_get(url, "tok-ana", memo, read) == (200, ana)
        assert conditional_get(url, "tok-ana", memo, read) == (200, ana)
        assert (reads, github.not_modified) == ([200], 1)
        assert list(memo) == [url]
        assert conditional_get(url, "nope", memo, read) == (401, None)


def test_conditional_get_keeps_nothing_without_an_etag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("tadu.conditional_get.github_call", lambda *_a, **_k: GithubReply(200))
    memo: dict[str, tuple[str, int]] = {}
    assert conditional_get("u", "t", memo, lambda _reply: 7) == (200, 7)
    assert memo == {}


def test_code_exchange_grants_tokens_once() -> None:
    with fake_github({}) as github:
        sign_in = github.sign_in("https://board.example.com")
        grant = exchange_github_code(sign_in, "code-ana", "verifier")
        assert grant is not None
        assert grant.token.startswith("tok-ana~")
        assert grant.refresh_token is not None
        assert grant.refresh_token.startswith("ref-ana~")
        assert grant.expires is not None
        assert exchange_github_code(sign_in, "code-ana", "verifier") is None
        assert exchange_github_code(sign_in, "stale", "verifier") is None
        assert github.requests == ["POST /login/oauth/access_token"] * 3


def test_an_oauth_app_grant_never_expires() -> None:
    with fake_github({}) as github:
        github.expiring = False
        assert exchange_github_code(github.sign_in(), "code-ana", "verifier") == TokenGrant(
            "tok-ana~1"
        )


def test_the_token_endpoint_answering_an_error_page_grants_nothing() -> None:
    with fake_github({}) as github:
        github.token_endpoint_down = True
        assert exchange_github_code(github.sign_in(), "code-ana", "verifier") is None
        wrong = FakeGithub(github.url, {}).sign_in()
        object.__setattr__(wrong, "client_secret", "nope")
        assert exchange_github_code(wrong, "code-ana", "verifier") is None


def test_refresh_hands_out_a_new_pair_once() -> None:
    with fake_github({}) as github:
        sign_in = github.sign_in()
        first = exchange_github_code(sign_in, "code-ana", "verifier")
        assert first is not None
        assert first.refresh_token is not None
        renewed = refresh_github_token(sign_in, first.refresh_token)
        assert renewed is not None
        assert renewed.token != first.token
        assert renewed.refresh_token not in {None, first.refresh_token}
        with pytest.raises(SignedOutError):
            refresh_github_token(sign_in, first.refresh_token)


def test_refresh_after_the_app_is_revoked_signs_out() -> None:
    with fake_github({}) as github:
        sign_in = github.sign_in()
        grant = exchange_github_code(sign_in, "code-ana", "verifier")
        assert grant is not None
        assert grant.refresh_token is not None
        github.revoke_app("ana")
        with pytest.raises(SignedOutError):
            refresh_github_token(sign_in, grant.refresh_token)


def test_refresh_that_cannot_reach_github_tells_nothing() -> None:
    with fake_github({}) as github:
        sign_in = github.sign_in()
        grant = exchange_github_code(sign_in, "code-ana", "verifier")
        assert grant is not None
        assert grant.refresh_token is not None
        github.token_endpoint_down = True
        assert refresh_github_token(sign_in, grant.refresh_token) is None
        github.token_endpoint_down = False
        assert refresh_github_token(sign_in, grant.refresh_token) is not None


def test_login_of_a_token() -> None:
    with fake_github({}) as github:
        assert github_user_login(github.sign_in(), "tok-Ana-Dev") == "Ana-Dev"
        assert github_user_login(github.sign_in(), "tok-revoked") is None
        assert github_user_login(github.sign_in(), "tok-nobody") is None


def test_repository_status() -> None:
    with fake_github({"ana": {"acme/shop", "acme/nopull"}}) as github:
        sign_in, access = github.sign_in(), TokenAccess()
        shop = (200, github.repo_id("acme/shop"), "acme/shop")
        assert repository_status(sign_in, "tok-ana", "acme/shop", access) == shop
        assert repository_status(sign_in, "tok-ana", "acme/shop", access) == shop
        assert github.not_modified == 1
        assert repository_status(sign_in, "tok-ana", "acme/vault", access) == (404, None, None)
        nopull = (404, github.repo_id("acme/nopull"), None)
        assert repository_status(sign_in, "tok-ana", "acme/nopull", access) == nopull
        assert repository_status(sign_in, "tok-ana", "acme/flaky", access) == (502, None, None)
        assert repository_status(sign_in, "tok-revoked", "acme/shop", access) == (401, None, None)


def test_a_renamed_repository_is_followed_to_its_new_name() -> None:
    with fake_github({"ana": {"acme/shop-v2"}}) as github:
        github.renamed["acme/shop"] = "acme/shop-v2"
        answer = repository_status(github.sign_in(), "tok-ana", "acme/shop", TokenAccess())
        assert answer == (200, github.repo_id("acme/shop-v2"), "acme/shop-v2")
        assert github.requests == ["GET /api/repos/acme/shop", "GET /api/repos/acme/shop-v2"]
