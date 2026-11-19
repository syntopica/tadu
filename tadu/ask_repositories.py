"""Ask GitHub about single repositories, a few at a time."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.repository_status import repository_status
from tadu.sign_in_settings import PARALLEL_REQUESTS
from tadu.signed_out_error import SignedOutError

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn
    from tadu.token_access import TokenAccess


def ask_repositories(
    sign_in: GithubSignIn, token: str, names: list[str], access: TokenAccess
) -> dict[str, tuple[int, int | None, str | None]]:
    """Each name's status, GitHub id and current name, PARALLEL_REQUESTS at a time.

    Raise SignedOutError when GitHub refuses the token for any of them.
    """
    if not names:
        return {}
    with ThreadPoolExecutor(min(PARALLEL_REQUESTS, len(names))) as pool:
        answers = list(pool.map(lambda n: repository_status(sign_in, token, n, access), names))
    if any(status == HTTPStatus.UNAUTHORIZED for status, _, _ in answers):
        raise SignedOutError
    # keys: the names are asked once each.
    return dict(zip(names, answers, strict=True))
