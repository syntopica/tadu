"""Read the text of a board's saved sessions."""

from __future__ import annotations

import json

from tadu.stored_session import StoredSession

VERSION = 2
FIELDS = {"login": str, "expires": int, "sealed": str}


def parse_sessions(text: str) -> dict[str, StoredSession]:
    """Sealed sessions by id; ValueError for anything but the written shape.

    The shape is `{"version": 2, "sessions": {"<id>": {"login", "expires",
    "sealed"}}}`. Version 1 (before tokens were renewed) is not read: everyone signed
    in then signs in once more.
    """
    data = json.loads(text)
    sessions = data.get("sessions") if isinstance(data, dict) else None
    if (
        not isinstance(data, dict)
        or data.get("version") != VERSION
        or not isinstance(sessions, dict)
    ):
        msg = f'expected {{"version": {VERSION}, "sessions": {{...}}}}'
        raise ValueError(msg)
    for key, row in sessions.items():
        if not isinstance(row, dict) or any(type(row.get(f)) is not t for f, t in FIELDS.items()):
            msg = f"session {key[:8]} needs login, expires and sealed"
            raise ValueError(msg)
    # keys: JSON object keys are unique once parsed.
    return {
        key: StoredSession(row["login"], row["expires"], row["sealed"])
        for key, row in sessions.items()
    }
