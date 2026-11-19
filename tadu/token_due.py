"""Whether a session's GitHub token should be renewed before it is used."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.sign_in_settings import REFRESH_MARGIN_SECONDS

if TYPE_CHECKING:
    from tadu.board_session import BoardSession


def token_due(session: BoardSession, now: float) -> bool:
    """True with no usable token, or one that expires within REFRESH_MARGIN_SECONDS."""
    expires = session.token_expires
    return session.token is None or (
        expires is not None and expires - now <= REFRESH_MARGIN_SECONDS
    )
