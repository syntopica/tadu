"""An organization in the workspace."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrganizationEntry:
    """An organization id and display name."""

    id: str
    name: str
