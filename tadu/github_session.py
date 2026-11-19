"""The HTTP session tadu asks GitHub's API with."""

from __future__ import annotations

from tadu.same_origin_redirects import SameOriginRedirects


class GithubSession(SameOriginRedirects):
    """A requests session whose redirects stay on GitHub's host (see SameOriginRedirects)."""
