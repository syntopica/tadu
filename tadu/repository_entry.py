"""A repository registered in the workspace."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryEntry:
    """A repository key, its optional remote, the backlog folder inside it and its access.

    `access` is the most a tool may do to it through the workspace: read, write or admin.
    """

    key: str
    remote: str | None
    backlog: str = "."
    access: str = "admin"
