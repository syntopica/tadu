"""Resolve a path once and accept it only when it stays under the root."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def resolve_inside_root(target: Path, root: Path) -> Path | None:
    """The target with symlinks and ".." resolved, or None when it lies outside the root."""
    resolved = target.resolve()
    return resolved if resolved.is_relative_to(root.resolve()) else None
