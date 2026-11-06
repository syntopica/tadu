"""Run a command whose reader may stop reading early, as `tadu list | head` does."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def quiet_broken_pipe(run: Callable[[], int]) -> int:
    """Run and flush; a closed stdout ends the command quietly with status 0.

    Output that no longer has a reader is not an error of the command. Pointing
    stdout at the null device keeps the interpreter's own final flush from
    printing a second traceback.
    """
    try:
        status = run()
        sys.stdout.flush()
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 0
    return status
