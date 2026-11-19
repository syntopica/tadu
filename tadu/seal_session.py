"""Seal a session with its cookie."""

from __future__ import annotations

import base64
import json
from typing import TYPE_CHECKING

from cryptography.fernet import Fernet

from tadu.session_secret import session_secret
from tadu.stored_session import StoredSession

if TYPE_CHECKING:
    from tadu.board_session import BoardSession


def seal_session(cookie: str, session: BoardSession) -> StoredSession:
    """The session encrypted and authenticated with Fernet, under a key derived from the cookie."""
    key = base64.urlsafe_b64encode(session_secret(cookie, "key"))
    payload = {
        "login": session.login,
        "expires": session.expires,
        "token": session.token,
        "token_expires": session.token_expires,
        "refresh_token": session.refresh_token,
    }
    sealed = Fernet(key).encrypt(json.dumps(payload).encode()).decode()
    return StoredSession(session.login, session.expires, sealed)
