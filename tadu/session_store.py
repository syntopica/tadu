"""The signed-in sessions of one board server, kept so they survive a restart."""

from __future__ import annotations

import secrets
import sys
import threading
import time
from typing import TYPE_CHECKING

from tadu.board_session import BoardSession
from tadu.live_sessions import live_sessions
from tadu.load_sessions import load_sessions
from tadu.open_session import open_session
from tadu.save_sessions import save_sessions
from tadu.seal_session import seal_session
from tadu.session_id import session_id
from tadu.sign_in_settings import IDLE_TIMEOUT_SECONDS

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.token_grant import TokenGrant


class SessionStore:
    """Sessions by an id derived from their cookie, each sealed with the cookie.

    With a `path`, sessions are read from it at the start and written to it whenever
    one begins, changes or ends, so a restart keeps everyone signed in. Neither memory
    nor the file holds a cookie or a token in the clear: without the cookie the browser
    keeps, a session cannot be found, used or opened. A file that cannot be read is set
    aside (everyone signs in again, and `problem` says why); one that cannot be written
    keeps sessions in memory until the next restart, with a warning.
    """

    def __init__(self, path: Path | None = None, idle_timeout: int = IDLE_TIMEOUT_SECONDS) -> None:
        """Start from the live sessions saved at `path`; each ends after `idle_timeout` unused.

        Saved sessions with longer to last than the idle timeout end; `shortened` counts them.
        """
        self._path, self.idle_timeout = path, idle_timeout
        loaded = load_sessions(path, time.time(), idle_timeout)
        self._sessions, self._text, self.problem, self.shortened = loaded
        self._locks: dict[str, threading.Lock] = {}
        self._lock = threading.Lock()
        self._failing = False

    def create(self, login: str, grant: TokenGrant, now: float) -> str:
        """Start a session for the login with GitHub's grant and return the cookie value.

        Ended sessions are dropped, and so is the login's oldest beyond SESSIONS_PER_LOGIN.
        """
        cookie = secrets.token_urlsafe(32)
        key = session_id(cookie)
        session = BoardSession(
            key,
            login,
            int(now) + self.idle_timeout,
            grant.token,
            grant.expires,
            grant.refresh_token,
        )
        with self._lock:
            self._sessions = live_sessions(self._sessions, login, now)
            self._sessions[key] = seal_session(cookie, session)
            self._locks = {k: lock for k, lock in self._locks.items() if k in self._sessions}
            self._save()
        return cookie

    def find(self, cookie: str | None, now: float) -> BoardSession | None:
        """The live session of a cookie value, opened, else None."""
        if not cookie:
            return None
        with self._lock:
            stored = self._sessions.get(session_id(cookie))
        if stored is None or stored.expires <= now:
            return None
        return open_session(cookie, stored)

    def save(self, cookie: str, session: BoardSession) -> None:
        """Keep a changed session (a renewed token, a later end), if it has not ended."""
        with self._lock:
            if session.id in self._sessions:
                self._sessions[session.id] = seal_session(cookie, session)
                self._save()

    def drop(self, cookie: str | None) -> None:
        """End the session of a cookie value, if there is one, on disk too."""
        if not cookie:
            return
        key = session_id(cookie)
        with self._lock:
            self._locks.pop(key, None)
            if self._sessions.pop(key, None) is not None:
                self._save()

    def lock(self, cookie: str) -> threading.Lock:
        """The lock that lets one request at a time renew the session's token."""
        with self._lock:
            return self._locks.setdefault(session_id(cookie), threading.Lock())

    def _save(self) -> None:
        """Write the sessions down; the caller holds the lock.

        A failure is reported when saving starts to fail, not at every sign-in after.
        """
        if self._path is None:
            return
        try:
            self._text = save_sessions(self._path, self._text, self._sessions)
        except OSError as error:
            if not self._failing:
                sys.stderr.write(
                    f"tadu board: warning: cannot save sessions ({error}); "
                    "they last until the board restarts\n"
                )
            self._failing = True
        else:
            self._failing = False
