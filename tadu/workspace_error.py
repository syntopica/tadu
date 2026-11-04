"""A workspace or local configuration problem."""

from __future__ import annotations


class WorkspaceError(Exception):
    """Raised with a message naming the file, table or key at fault."""
