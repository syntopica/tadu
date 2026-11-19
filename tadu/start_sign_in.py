"""Send a person to GitHub to sign in."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from oauthlib.oauth2 import WebApplicationClient

from tadu.board_answer import BoardAnswer
from tadu.github_oauth import github_oauth
from tadu.set_cookie import set_cookie
from tadu.sign_in_settings import (
    CALLBACK_PATH,
    OAUTH_SCOPE,
    PKCE_METHOD,
    STATE_COOKIE,
    STATE_SECONDS,
)

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn


def start_sign_in(sign_in: GithubSignIn) -> BoardAnswer:
    """Redirect to GitHub's authorize page with a fresh `state` and PKCE challenge.

    requests-oauthlib builds the URL and draws the state; oauthlib draws the PKCE code
    verifier, whose SHA-256 challenge goes to GitHub. Both the state and the verifier
    are kept in this browser's sign-in cookie (`state.verifier`): the callback accepts
    only the state this browser was given, so nobody can sign another person in to
    their own account, and a code that leaked (from a log, a history, a Referer) is
    worthless without the verifier. `repo` is asked for, which an OAuth App needs to
    see private repositories and a GitHub App ignores. GitHub shows its account picker
    every time (`prompt=select_account`): on a shared computer, whoever is still signed
    in to GitHub in the browser is not taken for the next person without a click.
    """
    pkce, method = WebApplicationClient(sign_in.client_id), PKCE_METHOD
    verifier = pkce.create_code_verifier(64)
    oauth = github_oauth(sign_in, sign_in.public_url + CALLBACK_PATH)
    oauth.scope = [OAUTH_SCOPE]
    url, state = oauth.authorization_url(
        f"{sign_in.web_url}/login/oauth/authorize",
        allow_signup="false",
        prompt="select_account",
        code_challenge=pkce.create_code_challenge(verifier, method),
        code_challenge_method=method,
    )
    cookie = set_cookie(sign_in, STATE_COOKIE, f"{state}.{verifier}", STATE_SECONDS)
    return BoardAnswer(
        (HTTPStatus.FOUND, b"", "text/plain; charset=utf-8"), (("Location", url), cookie)
    )
