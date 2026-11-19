"""Run one git command to completion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.git_process import git_process
from tadu.history_error import HistoryError

if TYPE_CHECKING:
    from pathlib import Path


def run_git(root: Path, args: tuple[str, ...], data: str = "") -> str:
    """Git's standard output for `args` in `root`, given `data` on standard input.

    HistoryError with the first line git printed, without its `fatal: `, when git fails.
    """
    with git_process(root, args) as process:
        out, err = process.communicate(data.encode())
    if process.returncode:
        said = err.decode(errors="replace").strip().splitlines()
        msg = said[0].removeprefix("fatal: ") if said else f"git {args[0]} failed"
        raise HistoryError(msg)
    return out.decode(errors="replace")
