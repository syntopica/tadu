"""Write a board's sessions to its file."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.backlog_unchanged import backlog_unchanged
from tadu.create_file_exclusively import create_file_exclusively
from tadu.render_sessions import render_sessions
from tadu.write_file_atomically import write_file_atomically

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.stored_session import StoredSession


def save_sessions(path: Path, before: str | None, sessions: dict[str, StoredSession]) -> str:
    """Write the sessions and return the text written.

    `before` is what the board last read or wrote there (None: no file yet). A new file
    is readable by its owner only; a file that changed meanwhile is left alone, since
    another process owns it. Raise OSError when it cannot be written.
    """
    text = render_sessions(sessions)
    if before is None:
        create_file_exclusively(path, text, mode=0o600)
    elif backlog_unchanged((path, before)):
        write_file_atomically(path, text)
    else:
        msg = f"{path} changed outside this board"
        raise OSError(msg)
    return text
