"""The OAuth session tadu trades codes and refresh tokens with."""

from __future__ import annotations

from requests_oauthlib import OAuth2Session

from tadu.same_origin_redirects import SameOriginRedirects


class GithubOAuthSession(SameOriginRedirects, OAuth2Session):
    """requests-oauthlib's session, whose redirects stay on GitHub's host.

    The token requests carry the client secret and refresh tokens in their body, which
    a 307 or 308 redirect would send on; SameOriginRedirects stops it before it leaves.
    """
