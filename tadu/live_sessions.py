"""The sessions to keep when one more begins."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.sign_in_settings import SESSIONS_PER_LOGIN

if TYPE_CHECKING:
    from tadu.stored_session import StoredSession


def live_sessions(
    sessions: dict[str, StoredSession], login: str, now: float
) -> dict[str, StoredSession]:
    """Those that have not ended, without the login's oldest beyond SESSIONS_PER_LOGIN - 1.

    So signing in again and again cannot fill the memory or the file.
    """
    live = {k: s for k, s in sessions.items() if s.expires > now}
    own = sorted((s.expires, k) for k, s in live.items() if s.login.lower() == login.lower())
    for _, key in own[: max(0, len(own) - SESSIONS_PER_LOGIN + 1)]:
        del live[key]
    return live
