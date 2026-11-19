"""A repository `tadu changes` reads."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class ChangeRepository:
    """The label its items carry, its project, its checkout and the backlog's folder in it.

    The project is None for a repository outside one, or read from a path.
    """

    repository: str
    project: str | None
    root: Path
    backlog: str = "."
