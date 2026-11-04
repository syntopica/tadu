"""A person in the workspace."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PersonEntry:
    """A person id, display name and optional organization id."""

    id: str
    name: str
    organization: str | None
