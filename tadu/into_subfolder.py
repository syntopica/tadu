"""Send a request for a board's subfolder, without its slash, to the subfolder."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.board_answer import BoardAnswer

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn


def into_subfolder(sign_in: GithubSignIn, path: str) -> BoardAnswer:
    """308 to `/tadu/` for `/tadu`, the query string kept.

    The page's links are relative: from `/tadu` they would leave the subfolder.
    """
    query = path.partition("?")[2]
    location = f"{sign_in.base_path}/" + (f"?{query}" if query else "")
    return BoardAnswer(
        (HTTPStatus.PERMANENT_REDIRECT, b"", "text/plain; charset=utf-8"), (("Location", location),)
    )
