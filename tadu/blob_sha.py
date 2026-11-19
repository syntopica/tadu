"""The hash git gives a file's bytes."""

from __future__ import annotations

import hashlib


def blob_sha(data: bytes) -> str:
    """The SHA-1 of a git blob of `data`, as git and GitHub name it."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data, usedforsecurity=False).hexdigest()
