"""What GitHub grants when someone signs in or a token is renewed."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenGrant:
    """The access token, when it expires (None: never) and the token that renews it.

    A GitHub App's user tokens expire after 8 hours and come with a refresh token; an
    OAuth App's never expire and have none.
    """

    token: str
    expires: int | None = None
    refresh_token: str | None = None
