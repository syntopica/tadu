"""What a board knows about GitHub access, per session."""

from __future__ import annotations

import threading

from tadu.sign_in_settings import IDLE_TIMEOUT_SECONDS
from tadu.token_access import TokenAccess


class AccessStore:
    """One TokenAccess per session, and the operator warnings already given.

    Kept in memory only, by session id (derived from the cookie), never by token.
    """

    def __init__(self) -> None:
        """Start knowing nothing."""
        self._tokens: dict[str, TokenAccess] = {}
        self._warned: set[str] = set()
        self._lock = threading.Lock()

    def for_session(self, key: str, now: float) -> TokenAccess:
        """The session's record, by session id, created on first use.

        Records unused for a session's idle timeout are dropped: their session has ended.
        """
        with self._lock:
            self._tokens = {
                k: a for k, a in self._tokens.items() if now - a.used_at < IDLE_TIMEOUT_SECONDS
            }
            access = self._tokens.setdefault(key, TokenAccess())
            access.used_at = now
            return access

    def forget(self, key: str) -> None:
        """Drop what is known for a session that ended."""
        with self._lock:
            self._tokens.pop(key, None)

    def first_warning(self, message: str) -> bool:
        """True the first time a warning is given, so the operator reads it once."""
        with self._lock:
            new = message not in self._warned
            self._warned.add(message)
            return new
