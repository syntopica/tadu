"""Read one page of a token's repository list."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.can_pull import can_pull
from tadu.last_page import last_page

if TYPE_CHECKING:
    from tadu.github_reply import GithubReply


def list_page_names(reply: GithubReply) -> tuple[tuple[tuple[str, int], ...], int]:
    """Each readable repository as (`owner/name` in lowercase, GitHub id), and the page count.

    An entry without a name and a whole-number id is left out.
    """
    entries = reply.body if isinstance(reply.body, list) else []
    named = tuple(
        (entry["full_name"].lower(), entry["id"])
        for entry in entries
        if can_pull(entry)
        and isinstance(entry.get("full_name"), str)
        and type(entry.get("id")) is int
    )
    return named, last_page(reply.links)
