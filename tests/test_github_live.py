"""The GitHub client against the real API, read only; run with `TADU_LIVE_GITHUB_TOKEN=... pytest -m live`."""

import os
from http import HTTPStatus

import pytest

from tadu.github_call import github_call
from tadu.github_sign_in import GithubSignIn
from tadu.github_user_login import github_user_login
from tadu.listed_repositories import listed_repositories
from tadu.repository_status import repository_status
from tadu.signed_out_error import SignedOutError
from tadu.token_access import TokenAccess

TOKEN = os.environ.get("TADU_LIVE_GITHUB_TOKEN", "")
pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(not TOKEN, reason="TADU_LIVE_GITHUB_TOKEN is not set"),
]
SIGN_IN = GithubSignIn("id", "secret", "http://127.0.0.1:1")


def test_the_token_names_its_user_and_an_unchanged_answer_is_a_304() -> None:
    first = github_call(f"{SIGN_IN.api_url}/user", TOKEN)
    assert github_user_login(SIGN_IN, TOKEN)
    assert (
        github_call(f"{SIGN_IN.api_url}/user", TOKEN, etag=first.etag).status
        == HTTPStatus.NOT_MODIFIED
    )


def test_the_repository_list_is_read_and_a_revoked_token_signs_out() -> None:
    names, failed = listed_repositories(SIGN_IN, TOKEN, TokenAccess())
    assert failed is None
    assert all("/" in name for name in names)
    with pytest.raises(SignedOutError):
        listed_repositories(SIGN_IN, "ghp_" + "0" * 36, TokenAccess())


def test_a_public_repository_reads_and_a_missing_one_does_not() -> None:
    access = TokenAccess()
    assert repository_status(SIGN_IN, TOKEN, "octocat/Hello-World", access)[0] == HTTPStatus.OK
    assert (
        repository_status(SIGN_IN, TOKEN, "octocat/no-such-repository-xyz", access)[0]
        == HTTPStatus.NOT_FOUND
    )
