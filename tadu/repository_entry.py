"""A repository registered in the workspace."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryEntry:
    """A repository key, its optional remote and the backlog folder inside it.

    `github_id`, when the workspace gives one, is the id its GitHub remote must name.
    """

    key: str
    remote: str | None
    backlog: str = "."
    github_id: int | None = None
