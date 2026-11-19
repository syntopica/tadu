"""What GitHub answered."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GithubReply:
    """The status, the parsed JSON body (None when there is none) and the headers tadu reads.

    `etag` lets the next request ask "changed since?"; `links` are the pagination links
    of the Link header by relation, as `requests` parses them.
    """

    status: int
    body: object = None
    etag: str | None = None
    links: dict[str, dict[str, str]] = field(default_factory=dict)
