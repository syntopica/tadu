"""The hash a caller keeps to prove it saw the current file."""

from __future__ import annotations

import hashlib


def text_hash(text: str) -> str:
    """SHA-256 hex digest of the text's UTF-8 bytes."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
