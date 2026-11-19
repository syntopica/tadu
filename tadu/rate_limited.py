"""Refuse a sign-in request that comes too often."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.board_answer import BoardAnswer
from tadu.sign_in_settings import CALLBACK_PATH, SIGN_IN_PATH
from tadu.text_response import text_response

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn

LIMITED_PATHS = (SIGN_IN_PATH, CALLBACK_PATH)


def rate_limited(sign_in: GithubSignIn, path: str, address: str) -> BoardAnswer | None:
    """429 with Retry-After when the address used the path too often; None otherwise.

    Only the paths that start and finish a sign-in are limited: each finish makes the
    board ask GitHub and write a session. The rest needs a session already.
    """
    route = path.partition("?")[0]
    if route not in LIMITED_PATHS:
        return None
    wait = sign_in.limiter.hit(route, address)
    if wait is None:
        return None
    message = f"Too many sign-in attempts from your address. Try again in {wait} seconds."
    return BoardAnswer(
        text_response(HTTPStatus.TOO_MANY_REQUESTS, message), (("Retry-After", str(wait)),)
    )
