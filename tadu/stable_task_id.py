"""A task id derived from text, for items that never had one."""

from __future__ import annotations

import hashlib
import uuid


def stable_task_id(*parts: str) -> str:
    """t- and a UUID4 built from a hash of the parts, so converting twice gives the same id."""
    digest = hashlib.sha256("\0".join(parts).encode()).digest()
    return f"t-{uuid.UUID(bytes=digest[:16], version=4)}"
