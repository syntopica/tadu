"""A stable fingerprint of a workspace directory."""

from __future__ import annotations

import hashlib
from pathlib import Path


def workspace_digest(workspace: str | Path) -> str:
    """The SHA-256 hex digest of the workspace's resolved path."""
    resolved = Path(workspace).expanduser().resolve()
    return hashlib.sha256(str(resolved).encode()).hexdigest()
