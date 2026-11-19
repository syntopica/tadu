"""An OAuth client for GitHub's sign-in, from requests-oauthlib."""

from __future__ import annotations

from typing import TYPE_CHECKING

import requests

from tadu.github_oauth_session import GithubOAuthSession

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn


def github_oauth(sign_in: GithubSignIn, redirect_uri: str | None = None) -> GithubOAuthSession:
    """A session for the app, whose token answers count only when GitHub answered 200.

    Its redirects stay on GitHub's origin (GithubOAuthSession), so neither the client
    secret nor a refresh token is ever sent to another host.

    GitHub reports a refused code or refresh token in a 200 answer, which oauthlib turns
    into an OAuth2Error; any other status (GitHub down, a proxy's error page) raises
    requests.HTTPError instead, so it is never taken for a refusal. No scope is given:
    oauthlib would refuse a GitHub App's grant, which carries none.
    """
    oauth = GithubOAuthSession(sign_in.client_id, redirect_uri=redirect_uri)

    def only_answers(response: requests.Response) -> requests.Response:
        if response.status_code != requests.codes.ok:
            raise requests.HTTPError(response=response)
        return response

    oauth.register_compliance_hook("access_token_response", only_answers)
    oauth.register_compliance_hook("refresh_token_response", only_answers)
    return oauth
