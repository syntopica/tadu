"""Build a repository entry from its table row."""

from __future__ import annotations

from pathlib import PurePath

from tadu.optional_text import optional_text
from tadu.repository_entry import RepositoryEntry
from tadu.required_text import required_text
from tadu.workspace_error import WorkspaceError


def parse_repository(row: dict[str, object]) -> RepositoryEntry:
    """Read key, remote and backlog; the backlog must stay inside the repository."""
    key = required_text(row, "repository", "key")
    backlog = optional_text(row, "repository", "backlog") or "."
    path = PurePath(backlog)
    if path.is_absolute() or ".." in path.parts:
        msg = f"repository {key}: backlog must be a relative path inside the repository"
        raise WorkspaceError(msg)
    return RepositoryEntry(key, optional_text(row, "repository", "remote"), backlog)
