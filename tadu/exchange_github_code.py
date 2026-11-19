"""Trade an OAuth code for GitHub tokens."""

from __future__ import annotations

from typing import TYPE_CHECKING

import requests
from oauthlib.oauth2 import OAuth2Error

from tadu.github_call import TIMEOUT_SECONDS
from tadu.github_oauth import github_oauth
from tadu.sign_in_settings import CALLBACK_PATH
from tadu.token_grant_of import token_grant_of

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn
    from tadu.token_grant import TokenGrant


def exchange_github_code(sign_in: GithubSignIn, code: str, verifier: str) -> TokenGrant | None:
    """What GitHub grants for the code, through requests-oauthlib; None when it grants nothing.

    `verifier` is the PKCE code verifier whose challenge went to GitHub with the sign-in.
    """
    oauth = github_oauth(sign_in, sign_in.public_url + CALLBACK_PATH)
    try:
        token = oauth.fetch_token(
            f"{sign_in.web_url}/login/oauth/access_token",
            code=code,
            code_verifier=verifier,
            client_secret=sign_in.client_secret,
            include_client_id=True,
            timeout=TIMEOUT_SECONDS,
        )
    except (OAuth2Error, requests.RequestException):
        return None
    return token_grant_of(token)
