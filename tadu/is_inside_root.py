"""Whether a path, after symlinks and ".." are resolved, stays under the root."""

from __future__ import annotations

from pathlib import Path


def is_inside_root(target: Path, root: Path) -> bool:
    """True when the resolved target is the root or lies beneath it."""
    return target.resolve().is_relative_to(root.resolve())
