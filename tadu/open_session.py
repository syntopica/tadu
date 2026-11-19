"""Open a sealed session with the cookie that sealed it."""

from __future__ import annotations

import base64
import json
from typing import TYPE_CHECKING

from cryptography.fernet import Fernet, InvalidToken

from tadu.board_session import BoardSession
from tadu.session_id import session_id
from tadu.session_secret import session_secret

if TYPE_CHECKING:
    from tadu.stored_session import StoredSession


def open_session(cookie: str, stored: StoredSession) -> BoardSession | None:
    """The session, or None when it does not open with this cookie.

    That is when it was sealed with another cookie, was changed since (Fernet checks),
    or its clear login and end disagree with the sealed ones.
    """
    key = base64.urlsafe_b64encode(session_secret(cookie, "key"))
    try:
        data = json.loads(Fernet(key).decrypt(stored.sealed))
    except InvalidToken:
        return None
    if (data["login"], data["expires"]) != (stored.login, stored.expires):
        return None
    return BoardSession(
        session_id(cookie),
        data["login"],
        data["expires"],
        data["token"],
        data["token_expires"],
        data["refresh_token"],
    )
