"""Renew a GitHub user token."""

from __future__ import annotations

from typing import TYPE_CHECKING

import requests
from oauthlib.oauth2 import OAuth2Error

from tadu.github_call import TIMEOUT_SECONDS
from tadu.github_oauth import github_oauth
from tadu.signed_out_error import SignedOutError
from tadu.token_grant_of import token_grant_of

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn
    from tadu.token_grant import TokenGrant


def refresh_github_token(sign_in: GithubSignIn, refresh_token: str) -> TokenGrant | None:
    """The new tokens, through requests-oauthlib; None when GitHub could not be asked.

    GitHub hands out a new refresh token each time and the old one stops working. Raise
    SignedOutError when GitHub refuses to renew: the app's authorization was revoked,
    or the refresh token expired.
    """
    oauth = github_oauth(sign_in)
    try:
        token = oauth.refresh_token(
            f"{sign_in.web_url}/login/oauth/access_token",
            refresh_token=refresh_token,
            client_id=sign_in.client_id,
            client_secret=sign_in.client_secret,
            timeout=TIMEOUT_SECONDS,
        )
    except OAuth2Error as error:
        raise SignedOutError from error
    except requests.RequestException:
        return None
    return token_grant_of(token)
