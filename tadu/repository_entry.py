"""A repository registered in the workspace."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryEntry:
    """A repository key, its optional remote and the backlog folder inside it."""

    key: str
    remote: str | None
    backlog: str = "."
