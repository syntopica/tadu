"""A person in the workspace."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PersonEntry:
    """A person id, display name, optional organization id and optional GitHub login."""

    id: str
    name: str
    organization: str | None
    github: str | None = None
