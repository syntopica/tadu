"""What GitHub answered, as a reply."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlsplit

import requests

from tadu.github_reply import GithubReply

if TYPE_CHECKING:
    from requests import Response


def github_answer(url: str, response: Response) -> GithubReply:
    """The reply to a request for `url`; one that ended on another origin counts as the redirect.

    An answer that still ended on another origin is the status of the redirect that led there,
    so nothing from elsewhere is read. A body that is not JSON reads as None.
    """
    asked, answered = urlsplit(url), urlsplit(response.url)
    if (asked.scheme, asked.netloc) != (answered.scheme, answered.netloc):
        return GithubReply(response.history[0].status_code if response.history else 0)
    try:
        body: object = response.json()
    except requests.JSONDecodeError:
        body = None
    return GithubReply(response.status_code, body, response.headers.get("ETag"), response.links)
