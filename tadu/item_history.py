"""The git commits that touched an item's line span."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def item_history(root: Path, path: str, line: int, end_line: int) -> str | None:
    """One `hash date author subject` line per commit; None when git cannot answer."""
    git = ["git", "-C", str(root)]
    log = [
        *git,
        "log",
        "--no-patch",
        "--date=short",
        "--format=%h %ad %an %s",
        f"-L{line},{end_line}:{path}",
    ]
    try:
        committed = subprocess.run(  # noqa: S603
            [*git, "show", f"HEAD:./{path}"], capture_output=True, check=False
        )
        # git log -L reads line numbers against HEAD, so only an unmodified file maps safely.
        if committed.returncode != 0 or committed.stdout != (root / path).read_bytes():
            return None
        done = subprocess.run(log, capture_output=True, text=True, check=False)  # noqa: S603
    except OSError:
        return None
    return done.stdout if done.returncode == 0 else None
