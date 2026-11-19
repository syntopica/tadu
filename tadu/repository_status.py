"""Ask GitHub whether a token can read one repository."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import quote

from tadu.conditional_get import conditional_get
from tadu.repository_answer import repository_answer

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn
    from tadu.token_access import TokenAccess


def repository_status(
    sign_in: GithubSignIn, token: str, name: str, access: TokenAccess
) -> tuple[int, int | None, str | None]:
    """The status of GET /repos/{owner}/{name}, and the id and name GitHub gave it.

    200 readable, 404 not, 0 unreachable: GitHub answers 404 for a repository the user
    cannot see, and 401 once the token is revoked or expired. A 200 whose permissions
    withhold `pull` counts as 404. A renamed repository is followed to its new name.
    The request carries the ETag of the last answer, so an unchanged one is a 304.
    """
    url = f"{sign_in.api_url}/repos/{quote(name)}"
    result = conditional_get(url, token, access.repositories, repository_answer)
    status, answer = result[0], result[1]
    if answer is None:
        return status, None, None
    readable, repository_id, now_named = answer
    return (status if readable else HTTPStatus.NOT_FOUND), repository_id, now_named
