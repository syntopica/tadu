"""Commit one file of a repository."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def commit_file(root: Path, name: str, message: str) -> bool:
    """Stage and commit only `name`; False when git refuses. Never pushes."""
    for command in (["add", "--", name], ["commit", "-m", message, "--", name]):
        done = subprocess.run(  # noqa: S603 - fixed git argv, no shell
            ["git", "-C", str(root), *command],  # noqa: S607
            capture_output=True,
            check=False,
        )
        if done.returncode != 0:
            return False
    return True
