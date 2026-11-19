"""A GET that asks GitHub only for what changed."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.github_call import github_call

if TYPE_CHECKING:
    from collections.abc import Callable

    from tadu.github_reply import GithubReply


def conditional_get[T](
    url: str, token: str, memo: dict[str, tuple[str, T]], read: Callable[[GithubReply], T]
) -> tuple[int, T | None]:
    """The status and what `read` takes from a 200 answer; None for any other status.

    The ETag remembered for the URL goes along as If-None-Match: a 304 (unchanged, and
    not counted against GitHub's rate limit) gives back the value read last time. A new
    200 answer is read and remembered with its ETag. Only what `read` returns is kept.
    """
    known = memo.get(url)
    reply = github_call(url, token, etag=known[0] if known else None)
    if reply.status == HTTPStatus.NOT_MODIFIED and known is not None:
        return HTTPStatus.OK, known[1]
    if reply.status != HTTPStatus.OK:
        return reply.status, None
    value = read(reply)
    if reply.etag:
        memo[url] = (reply.etag, value)
    return HTTPStatus.OK, value
