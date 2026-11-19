"""Write a board's sessions as text."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.parse_sessions import VERSION

if TYPE_CHECKING:
    from tadu.stored_session import StoredSession


def render_sessions(sessions: dict[str, StoredSession]) -> str:
    """Sealed sessions by id, sorted, as JSON."""
    # keys: the keys of a dict, sorted.
    rows = {
        key: {"login": s.login, "expires": s.expires, "sealed": s.sealed}
        for key, s in sorted(sessions.items())
    }
    return json.dumps({"version": VERSION, "sessions": rows}, indent=2) + "\n"
