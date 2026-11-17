"""Run a short-lived command with the cyclic garbage collector paused."""

from __future__ import annotations

import gc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def without_gc(run: Callable[[], int]) -> int:
    """Run it with collection paused, then restore the collector's previous state.

    Building tens of thousands of items makes the collector rescan the growing heap again and
    again, about half the run time at 27,500 tasks, to free nothing: a command's objects live
    until it exits. Not for the long-running board server.
    """
    enabled = gc.isenabled()
    gc.disable()
    try:
        return run()
    finally:
        if enabled:
            gc.enable()
