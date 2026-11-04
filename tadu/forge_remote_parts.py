"""Split a forge remote into host and path."""

from __future__ import annotations

import re

REMOTE_PATTERN = re.compile(
    r"(?:git@(?P<a>[^:/]+):|ssh://git@(?P<b>[^/]+)/|https://(?P<c>[^/]+)/)"
    r"(?P<path>[^/]+/[^/]+)"
)


def forge_remote_parts(remote: str) -> tuple[str, str] | None:
    """The (host, owner/name) of an ssh or https remote, else None."""
    text = remote.strip().removesuffix("/").removesuffix(".git")
    match = REMOTE_PATTERN.fullmatch(text)
    if match is None:
        return None
    host = match["a"] or match["b"] or match["c"]
    return host, match["path"]
