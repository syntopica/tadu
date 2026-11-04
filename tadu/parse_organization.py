"""Build an organization entry from its table row."""

from __future__ import annotations

from tadu.organization_entry import OrganizationEntry
from tadu.required_text import required_text


def parse_organization(row: dict[str, object]) -> OrganizationEntry:
    """Read id and name."""
    return OrganizationEntry(
        required_text(row, "organization", "id"),
        required_text(row, "organization", "name"),
    )
