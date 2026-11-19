"""Read GitHub's description of one repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.can_pull import can_pull

if TYPE_CHECKING:
    from tadu.github_reply import GithubReply


def repository_answer(reply: GithubReply) -> tuple[bool, int | None, str | None]:
    """Whether it may be read, its GitHub id and its `owner/name` now, in lowercase.

    After a rename or a transfer GitHub answers the old name with the repository under
    its new name, so the name read here can differ from the one asked about.
    """
    body = reply.body if isinstance(reply.body, dict) else {}
    repository_id = body.get("id")
    name = body.get("full_name")
    return (
        can_pull(reply.body),
        repository_id if type(repository_id) is int else None,
        name.lower() if isinstance(name, str) else None,
    )
