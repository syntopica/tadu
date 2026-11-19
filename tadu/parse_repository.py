"""Build a repository entry from its table row."""

from __future__ import annotations

from pathlib import PurePath

from tadu.access_levels import ACCESS_LEVELS
from tadu.optional_text import optional_text
from tadu.repository_entry import RepositoryEntry
from tadu.required_text import required_text
from tadu.workspace_error import WorkspaceError


def parse_repository(row: dict[str, object]) -> RepositoryEntry:
    """Read key, remote, backlog, github_id and access; the backlog must stay inside the repository."""
    key = required_text(row, "repository", "key")
    backlog = optional_text(row, "repository", "backlog") or "."
    path = PurePath(backlog)
    if path.is_absolute() or ".." in path.parts:
        msg = f"repository {key}: backlog must be a relative path inside the repository"
        raise WorkspaceError(msg)
    github_id = row.get("github_id")
    if github_id is not None and (type(github_id) is not int or github_id <= 0):
        msg = f"repository {key}: github_id must be a whole number above 0"
        raise WorkspaceError(msg)
    access = optional_text(row, "repository", "access") or "admin"
    if access not in ACCESS_LEVELS:
        msg = f"repository {key}: access must be one of {', '.join(ACCESS_LEVELS)}"
        raise WorkspaceError(msg)
    remote = optional_text(row, "repository", "remote")
    return RepositoryEntry(key, remote, backlog, access, github_id)
