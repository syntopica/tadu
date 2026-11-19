"""Start git, the one place tadu runs another program."""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import TYPE_CHECKING

from tadu.history_error import HistoryError

if TYPE_CHECKING:
    from pathlib import Path


def git_process(
    root: Path, args: tuple[str, ...], errors: int = subprocess.PIPE
) -> subprocess.Popen[bytes]:
    """Git started in `root` with `args`, its standard input, output and error piped.

    Callers pass fixed arguments. Paths and object names go on standard input, and a text to
    search for is attached to its option (`-S<text>`), so nothing taken from files or the user
    can be read as an option. A process that runs on while tadu talks to it passes
    `errors=subprocess.DEVNULL`: what it says on standard error is never read, and a full pipe
    would stop it. HistoryError without git.
    """
    # writes: nothing; shutil.which only looks git up on PATH
    git = shutil.which("git")
    if git is None:
        msg = "git is not installed"
        raise HistoryError(msg)
    pipe, argv = subprocess.PIPE, (git, *args)
    # argv is git's absolute path and fixed options; data is on stdin or attached to its option
    # LC_ALL=C: the messages tadu shows and tests are git's English ones, whatever the locale
    env = {**os.environ, "LC_ALL": "C"}
    return subprocess.Popen(argv, cwd=root, stdin=pipe, stdout=pipe, stderr=errors, env=env)  # noqa: S603
