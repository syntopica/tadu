"""What a board signing in with GitHub keeps beside the workspace between runs."""

from __future__ import annotations

from pathlib import Path

from tadu.read_github_ids import read_github_ids
from tadu.repository_pins import RepositoryPins
from tadu.session_store import SessionStore
from tadu.sign_in_settings import IDLE_TIMEOUT_SECONDS
from tadu.workspace_file_names import GITHUB_IDS_FILE, SESSIONS_FILE


def board_memory(
    workspace: str, idle_timeout: int = IDLE_TIMEOUT_SECONDS
) -> tuple[RepositoryPins, SessionStore]:
    """The repositories' GitHub ids and the sessions, from the workspace directory.

    The board needs that directory as surely as its configuration, so both survive
    whatever the board survives. Raise ValueError when the ids file is there but
    unreadable: it cannot be trusted, and a board that forgot it would trust the next
    repository to take a name. An unreadable sessions file only signs everyone out,
    which the store reports as its `problem`. Sessions end after `idle_timeout` seconds unused.
    """
    directory = Path(workspace)
    ids = directory / GITHUB_IDS_FILE
    sessions = SessionStore(directory / SESSIONS_FILE, idle_timeout)
    return RepositoryPins(ids, read_github_ids(ids)[0]), sessions
