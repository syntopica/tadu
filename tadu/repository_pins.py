"""Which GitHub repository each workspace repository is, kept across restarts."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from tadu.record_github_id import record_github_id

if TYPE_CHECKING:
    from pathlib import Path


class RepositoryPins:
    """The GitHub id of each workspace repository key.

    An id given as `github_id` in the workspace file is the repository's; otherwise the
    first id seen is learned and written to `path`, so a restart remembers it. Without
    a path (tests), ids are learned in memory only.
    """

    def __init__(self, path: Path | None = None, learned: dict[str, int] | None = None) -> None:
        """Start from the ids already learned, as read from `path`."""
        self._path = path
        self._learned = dict(learned or {})
        self._lock = threading.Lock()

    def admit(self, key: str, seen: int, given: int | None) -> int | None:
        """None when the id GitHub gave is the key's, else the id the key should have.

        The first id seen for a key without `given` is learned. Raise OSError or
        ValueError when it cannot be written down: unrecorded, it would not survive a
        restart.
        """
        if given is not None:
            return None if seen == given else given
        with self._lock:
            known = self._learned.get(key)
            if known is None and self._path is not None:
                self._learned = record_github_id(self._path, key, seen)
                known = self._learned[key]
            elif known is None:
                self._learned[key] = known = seen
        return None if seen == known else known
