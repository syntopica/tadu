"""Read what oauthlib made of GitHub's token answer."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.token_grant import TokenGrant

if TYPE_CHECKING:
    from collections.abc import Mapping


def token_grant_of(token: Mapping[str, object]) -> TokenGrant:
    """The access token, its expiry (oauthlib's `expires_at`) and the refresh token."""
    expires = token.get("expires_at")
    refresh = token.get("refresh_token")
    return TokenGrant(
        str(token["access_token"]),
        int(expires) if isinstance(expires, (int, float)) else None,
        refresh if isinstance(refresh, str) and refresh else None,
    )
