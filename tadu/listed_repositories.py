"""Every repository a GitHub login can read, from its repository list."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.conditional_get import conditional_get
from tadu.list_page_names import list_page_names
from tadu.sign_in_settings import LIST_PAGE_LIMIT, LIST_PAGE_SIZE, PARALLEL_REQUESTS
from tadu.signed_out_error import SignedOutError

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn
    from tadu.token_access import TokenAccess


def listed_repositories(
    sign_in: GithubSignIn, token: str, access: TokenAccess
) -> tuple[dict[str, int], int | None]:
    """Names and GitHub ids from GET /user/repos, 100 a page, and the status of a failed page.

    The first page says how many there are; the others are asked in parallel, each
    with its ETag. A list longer than LIST_PAGE_LIMIT pages is not read (the names come
    back empty, so each repository is asked about on its own): for someone who can read
    thousands of repositories, that is fewer requests. Raise SignedOutError on 401.
    """

    def page(number: int) -> tuple[int, tuple[tuple[tuple[str, int], ...], int] | None]:
        url = f"{sign_in.api_url}/user/repos?per_page={LIST_PAGE_SIZE}&page={number}"
        return conditional_get(url, token, access.pages, list_page_names)

    results = [page(1)]
    first = results[0][1]
    last = first[1] if first is not None else 1
    if last > LIST_PAGE_LIMIT:
        return {}, None
    if last > 1:
        with ThreadPoolExecutor(min(PARALLEL_REQUESTS, last - 1)) as pool:
            results += pool.map(page, range(2, last + 1))
    failed = [status for status, value in results if value is None]
    if HTTPStatus.UNAUTHORIZED in failed:
        raise SignedOutError
    if failed:
        return {}, failed[0]
    # keys: a name is one repository; one that moved between pages while they were read
    # comes twice, with the same id.
    return {name: id_ for _, value in results if value is not None for name, id_ in value[0]}, None
