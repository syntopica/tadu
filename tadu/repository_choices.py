"""The repositories a refusal offers, with their paths unless a team board asks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.visible_repositories import VISIBLE_REPOSITORIES

if TYPE_CHECKING:
    from pathlib import Path


def repository_choices(roots: dict[str, Path]) -> str:
    """`label (path)` for each root, or the labels alone on a board signing people in.

    There a path is the server's.
    """
    shown = VISIBLE_REPOSITORIES.get() is None
    return "; ".join(
        label if label == str(root) or not shown else f"{label} ({root})"
        for label, root in roots.items()
    )
