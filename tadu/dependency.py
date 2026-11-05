"""One `Depends on:` target as resolved against the loaded cards."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Dependency:
    """The target ID with its repository, state and column, all None when it was not found."""

    id: str
    repository: str | None
    state: str | None
    column: str | None
