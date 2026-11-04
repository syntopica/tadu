"""Flatten a project's roles table into (role, organization id) pairs."""

from __future__ import annotations

from tadu.text_list import text_list
from tadu.workspace_error import WorkspaceError


def parse_roles(value: object) -> tuple[tuple[str, str], ...]:
    """Pairs in table order, then list order; absent roles give no pairs."""
    if value is None:
        return ()
    if not isinstance(value, dict):
        msg = "project: roles must be a table"
        raise WorkspaceError(msg)
    return tuple(
        (role, org) for role, orgs in value.items() for org in text_list(orgs, "project", "roles")
    )
