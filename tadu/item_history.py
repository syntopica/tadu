"""The git commits that touched an item's line span."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def item_history(root: Path, path: str, line: int, end_line: int) -> str | None:
    """One `hash date author subject` line per commit; None when git cannot answer."""
    command = [
        "git",
        "-C",
        str(root),
        "log",
        "--no-patch",
        "--date=short",
        "--format=%h %ad %an %s",
        f"-L{line},{end_line}:{path}",
    ]
    try:
        done = subprocess.run(command, capture_output=True, text=True, check=False)  # noqa: S603
    except OSError:
        return None
    return done.stdout if done.returncode == 0 else None
