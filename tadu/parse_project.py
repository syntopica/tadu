"""Build a project entry from its table row."""

from __future__ import annotations

from tadu.optional_text import optional_text
from tadu.parse_roles import parse_roles
from tadu.project_entry import ProjectEntry
from tadu.required_text import required_text
from tadu.text_list import text_list


def parse_project(row: dict[str, object]) -> ProjectEntry:
    """Read key, name (default: the key), repositories and roles."""
    key = required_text(row, "project", "key")
    return ProjectEntry(
        key,
        optional_text(row, "project", "name") or key,
        text_list(row.get("repositories"), "project", "repositories"),
        parse_roles(row.get("roles")),
    )
