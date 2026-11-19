"""What is already known about one repository for one token."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.sign_in_settings import ACCESS_SECONDS, DENIED_SECONDS

if TYPE_CHECKING:
    from tadu.token_access import TokenAccess


def access_decision(access: TokenAccess, name: str, now: float) -> bool | None:
    """True or False while an answer is fresh, else None (GitHub must be asked).

    A fresh list that holds the repository says yes, whatever an older check said, so
    access given on GitHub shows at the next list. A single check's yes stays fresh for
    ACCESS_SECONDS, its no for DENIED_SECONDS.
    """
    if now - access.listed_at < ACCESS_SECONDS and name in access.listed:
        return True
    check = access.checks.get(name)
    if check is None:
        return None
    readable, checked, _ = check
    return readable if now - checked < (ACCESS_SECONDS if readable else DENIED_SECONDS) else None
