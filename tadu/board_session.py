"""One signed-in person of a board that signs in with GitHub."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoardSession:
    """Who is signed in, until when, and the GitHub tokens that act for them.

    `id` names the session (derived from its cookie). `expires` is when it ends unless
    it is used (Unix seconds). `token` is the GitHub access token, None while it has
    expired and GitHub could not be reached to refresh it; `token_expires` is when it
    expires (None: never, as an OAuth App's), and `refresh_token` renews it. None of
    it reaches the page.
    """

    id: str
    login: str
    expires: int
    token: str | None
    token_expires: int | None = None
    refresh_token: str | None = None
