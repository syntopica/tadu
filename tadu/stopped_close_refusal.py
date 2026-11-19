"""Refuse to migrate an item a stopped close left both open and closed."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.check_log_ids import check_log_ids

if TYPE_CHECKING:
    from pathlib import Path


def stopped_close_refusal(root: Path) -> str | None:
    """Why not, when doctor's T005 holds: the task would be migrated twice; else None."""
    split = [finding.line for finding in check_log_ids(root) if finding.code == "T005"]
    if not split:
        return None
    return (
        f"TODO.md:{split[0]}: an item is also closed in TODO_LOG.md (doctor's T005); run its "
        "tadu close again to finish it first, or the task would be migrated twice"
    )
