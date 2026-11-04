"""Link to a line of a file on its forge."""

from __future__ import annotations

from urllib.parse import quote

from tadu.forge_remote_parts import forge_remote_parts

BLOB_PREFIX = {"github.com": "blob", "gitlab.com": "-/blob"}


def forge_line_url(remote: str | None, path: str, line: int) -> str | None:
    """The GitHub or GitLab URL of path#line on HEAD, or None for any other remote."""
    parts = forge_remote_parts(remote) if remote else None
    if parts is None or parts[0] not in BLOB_PREFIX:
        return None
    host, repository = parts
    return f"https://{host}/{repository}/{BLOB_PREFIX[host]}/HEAD/{quote(path)}#L{line}"
