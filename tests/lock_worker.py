"""A writer for the lock tests, in a module of its own.

A spawned process imports the module its target lives in: this one imports only the lock,
where the test module would bring pytest and the rest of the suite's helpers along.
"""

import sys
import time
from pathlib import Path

from tadu.backlog_lock import backlog_lock


def add_under_lock(root: str, times: int, *, without_flock: bool) -> None:
    """Read, wait, write the counter: without the lock, two writers lose updates."""
    if without_flock:
        sys.modules["fcntl"] = None  # type: ignore[assignment]
    counter = Path(root) / "counter"
    for _ in range(times):
        with backlog_lock(Path(root)):
            value = int(counter.read_text())
            time.sleep(0.001)
            counter.write_text(str(value + 1))
