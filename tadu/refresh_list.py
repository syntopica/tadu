"""Read a session's repository list again."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.listed_repositories import listed_repositories

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn
    from tadu.token_access import TokenAccess


def refresh_list(sign_in: GithubSignIn, access: TokenAccess, token: str, now: float) -> bool:
    """Keep the fresh list on the session's access; False when it failed.

    A failure is recorded on the access. Raise SignedOutError on 401.
    """
    listed, failed = listed_repositories(sign_in, token, access)
    if failed is not None:
        access.failed, access.failed_at = failed, now
        return False
    access.listed, access.listed_at = listed, now
    return True
