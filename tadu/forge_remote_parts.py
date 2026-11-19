"""Split a forge remote into host and path."""

from __future__ import annotations

import re
from urllib.parse import urlsplit

SCP_LIKE = re.compile(r"(?:[^@/\s]+@)?(?P<host>[^:/\s]+):(?P<path>[^/\s].*)")
SCHEMES = frozenset({"https", "ssh", "git", "git+ssh"})


def forge_remote_parts(remote: str) -> tuple[str, str] | None:
    """The (host, path) of a remote, path as `owner/name` (or `group/sub/name`), else None.

    `scheme://[user@]host[:port]/path` is read by urllib, for https, ssh, git and git+ssh;
    the scp-like `[user@]host:path` that git also takes, by hand. The host is lowercased,
    without user or port; `.git` and slashes around the path go.
    """
    text = remote.strip()
    if "://" in text:
        parts = urlsplit(text)
        known = parts.scheme.lower() in SCHEMES
        host, path = (parts.hostname or "", parts.path) if known else ("", "")
    else:
        match = SCP_LIKE.fullmatch(text)
        host, path = (match["host"].lower(), match["path"]) if match else ("", "")
    path = path.strip("/").removesuffix(".git").strip("/")
    if not host or path.count("/") < 1 or "" in path.split("/"):
        return None
    return host, path
