"""A session as the board keeps it, in memory and on disk."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StoredSession:
    """The login and end in the clear, and the whole session sealed with its cookie.

    The clear copies only let the board drop ended sessions and count a login's
    sessions without the cookies; the sealed copy (a Fernet token: AES and HMAC) is the
    one that counts, and a record whose clear copies disagree with it does not open.
    """

    login: str
    expires: int
    sealed: str
