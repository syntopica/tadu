"""Ask git about the repository a backlog lives in."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def git_output(root: Path, *args: str) -> bytes | None:
    """What `git -C root ARGS` prints, as bytes, or None when git is missing or fails.

    Only `tadu migrate --recover` reads git: the Markdown backlog a migration removed
    survives only in the commits before it. The caller decodes, so it can tell a file that
    is not UTF-8 from one that is not there.
    """
    try:
        done = subprocess.run(  # noqa: S603 - git from PATH, tadu's own fixed arguments
            ["git", "-C", str(root), *args],  # noqa: S607
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    return done.stdout if done.returncode == 0 else None
