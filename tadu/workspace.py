"""The shared workspace description."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.organization_entry import OrganizationEntry
    from tadu.person_entry import PersonEntry
    from tadu.project_entry import ProjectEntry
    from tadu.repository_entry import RepositoryEntry


@dataclass(frozen=True)
class Workspace:
    """The directory it was loaded from and everything it registers."""

    root: Path
    repositories: tuple[RepositoryEntry, ...]
    projects: tuple[ProjectEntry, ...]
    organizations: tuple[OrganizationEntry, ...]
    people: tuple[PersonEntry, ...]
