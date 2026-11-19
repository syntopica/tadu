"""One request to GitHub's API."""

from __future__ import annotations

import requests
from oauthlib.oauth2 import OAuth2Error
from requests_oauthlib import OAuth2

from tadu.github_answer import github_answer
from tadu.github_reply import GithubReply
from tadu.github_session import GithubSession

TIMEOUT_SECONDS = 10
HEADERS = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}


def github_call(url: str, token: str, etag: str | None = None) -> GithubReply:
    """A GET with the token; with `etag`, a conditional GET.

    The token goes in the Authorization header as requests-oauthlib's bearer auth, so a
    credential in ~/.netrc for GitHub's host (the operator's, say) never replaces it.
    GitHub answers a conditional GET of something unchanged with 304 and no body, and
    does not count it against the rate limit. Redirects are followed only on GitHub's
    own origin (GithubSession): one to anywhere else is not followed, nothing is sent
    there, and the redirect's status is the answer. An answer that still ended on
    another origin would count as that status too, so nothing from elsewhere is read. A
    body that is not JSON reads as None; a GitHub that cannot be reached, or whose
    answer breaks off, answers status 0.
    """
    headers = HEADERS | ({"If-None-Match": etag} if etag is not None else {})
    try:
        with GithubSession() as session:
            # The token as an auth object, so requests never puts ~/.netrc in its place.
            session.auth = OAuth2(token={"access_token": token, "token_type": "Bearer"})
            response = session.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
    except (requests.RequestException, OAuth2Error):
        return GithubReply(0)
    return github_answer(url, response)
