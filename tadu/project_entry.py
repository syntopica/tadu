"""A project grouping repositories and organizations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectEntry:
    """A project; roles are (role, organization id) pairs in file order."""

    key: str
    name: str
    repositories: tuple[str, ...]
    roles: tuple[tuple[str, str], ...]
