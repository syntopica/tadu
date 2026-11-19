"""The GitHub id a token's fresh answers give a repository name."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.sign_in_settings import ACCESS_SECONDS

if TYPE_CHECKING:
    from tadu.token_access import TokenAccess


def seen_repository_id(access: TokenAccess, name: str, now: float) -> int | None:
    """The id from the fresh list, else from the check of the name, else None."""
    if now - access.listed_at < ACCESS_SECONDS and name in access.listed:
        return access.listed[name]
    check = access.checks.get(name)
    return check[2] if check is not None else None
