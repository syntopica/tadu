"""One request to GitHub's API that sends JSON."""

from __future__ import annotations

import requests
from oauthlib.oauth2 import OAuth2Error
from requests_oauthlib import OAuth2

from tadu.github_answer import github_answer
from tadu.github_call import HEADERS, TIMEOUT_SECONDS
from tadu.github_reply import GithubReply
from tadu.github_session import GithubSession


def github_send(url: str, token: str, body: dict[str, object], method: str = "POST") -> GithubReply:
    """A POST (or `method`) of `body` as JSON with the token, as github_call sends its GET.

    The same bearer auth (never ~/.netrc) and the same reading of the answer. A redirect is
    never followed, so a POST is neither sent twice nor turned into a GET: its status is the
    answer. A GitHub that cannot be reached, or whose answer breaks off, answers status 0.
    """
    try:
        with GithubSession() as session:
            session.auth = OAuth2(token={"access_token": token, "token_type": "Bearer"})
            response = session.request(
                method,
                url,
                json=body,
                headers=HEADERS,
                timeout=TIMEOUT_SECONDS,
                allow_redirects=False,
            )
    except (requests.RequestException, OAuth2Error):
        return GithubReply(0)
    return github_answer(url, response)
