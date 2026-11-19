"""Read the sessions a board saved."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.parse_sessions import parse_sessions
from tadu.read_text_exact import read_text_exact
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.stored_session import StoredSession


def load_sessions(
    path: Path | None, now: float, idle_timeout: int
) -> tuple[dict[str, StoredSession], str | None, str | None, int]:
    """Live sessions, the text read (None: no file), why none was read, how many ended.

    Ended are the saved sessions with longer to last than `idle_timeout`. A file that cannot be read or is not in the written shape gives no sessions and a
    problem to report: everyone signs in again, which is safe. A saved session with more
    time left than the idle timeout (it was shortened since) ends, as it would have.
    """
    if path is None or not path.exists():
        return {}, None, None, 0
    try:
        text = read_text_exact(path)
    except UnreadableFileError as error:
        return {}, None, f"{path}: {error}; everyone signs in again", 0
    try:
        saved = parse_sessions(text)
    except ValueError as error:
        return {}, text, f"{path}: {error}; everyone signs in again", 0
    live = {k: s for k, s in saved.items() if s.expires > now}
    # keys: the live sessions, less those the idle timeout has ended
    kept = {k: s for k, s in live.items() if s.expires - now <= idle_timeout}
    return kept, text, None, len(live) - len(kept)
