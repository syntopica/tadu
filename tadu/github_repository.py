"""The GitHub repository a workspace repository's remote names, if any."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tadu.forge_remote_parts import forge_remote_parts
from tadu.sign_in_settings import GITHUB_HOST

if TYPE_CHECKING:
    from tadu.repository_entry import RepositoryEntry

# GitHub's own rules: an owner is letters, digits and hyphens, not first; a repository
# name letters, digits, `.`, `_` and `-`, but not `.` or `..`.
NAME = re.compile(r"[a-z0-9][a-z0-9-]*/(?!\.{1,2}$)[a-z0-9._-]+")


def github_repository(entry: RepositoryEntry) -> str | None:
    """`owner/name` in lowercase when the remote is on github.com, else None.

    GitHub has no subgroups: a longer path (a link into the repository, say) is no
    remote, and neither is a path GitHub would not take as a name, so nothing but a
    repository of the API is ever asked about with a person's token.
    """
    parts = forge_remote_parts(entry.remote) if entry.remote else None
    if parts is None or parts[0] != GITHUB_HOST:
        return None
    name = parts[1].lower()
    return name if NAME.fullmatch(name) else None
