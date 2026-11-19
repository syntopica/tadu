"""Redirects that never leave the host a request was sent to."""

from __future__ import annotations

from typing import TYPE_CHECKING, override
from urllib.parse import urljoin, urlsplit

import requests

if TYPE_CHECKING:
    from requests import PreparedRequest, Response

DEFAULT_PORTS = {"http": 80, "https": 443}


class SameOriginRedirects(requests.Session):
    """A session that follows a redirect only to the scheme, host and port it is on.

    requests would follow a redirect anywhere: it drops the Authorization header when
    the host changes, but a 307 or 308 sends the body again, client secret and refresh
    token included, and the other host is contacted all the same. Here the target is
    checked in requests' own hook, `get_redirect_target`, before anything is sent: a
    redirect to another origin is not followed, and the redirect itself is the answer.
    Credentials stay the request's own: nothing is taken from ~/.netrc (`rebuild_auth`).
    """

    @override
    def get_redirect_target(self, resp: Response) -> str | None:
        """The redirect's target when it has the same origin as the response, else None."""
        target = super().get_redirect_target(resp)
        if target is None:
            return None
        here, there = self.origin(resp.url), self.origin(urljoin(resp.url, target))
        return target if here is not None and here == there else None

    @override
    def rebuild_auth(self, prepared_request: PreparedRequest, response: Response) -> None:
        """Keep the request's own credentials on a same-origin redirect, drop them otherwise.

        requests would put credentials from ~/.netrc for the new URL in place of the
        request's own, even on the same host: the operator's GitHub credentials would
        then answer for a person's token. Here ~/.netrc is never read. Should a redirect
        to another origin ever get this far (get_redirect_target refuses it), the
        request's Authorization goes, so the two guards do not rely on each other.
        """
        before, after = response.request.url, prepared_request.url
        if before is None or after is None or self.origin(before) != self.origin(after):
            prepared_request.headers.pop("Authorization", None)

    @staticmethod
    def origin(url: str) -> tuple[str, str, int] | None:
        """Scheme, host and port (the scheme's default when none is written); None if unclear."""
        parts = urlsplit(url)
        scheme = parts.scheme.lower()
        try:
            port = parts.port or DEFAULT_PORTS.get(scheme)
        except ValueError:
            return None
        if port is None or not parts.hostname:
            return None
        return scheme, parts.hostname.lower(), port
