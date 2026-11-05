"""Run `git blame --line-porcelain` on one file of a checkout."""

from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def git_blame_output(root: Path, path: str) -> str | None:
    """The blame text of the working-tree file, or None when git cannot blame it."""
    git = shutil.which("git")
    if git is None:
        return None
    try:
        # Fixed argument list, no shell; the path comes from the scanned backlog.
        done = subprocess.run(  # noqa: S603
            [git, "-C", str(root), "blame", "--line-porcelain", "--", path],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.stdout if done.returncode == 0 else None
