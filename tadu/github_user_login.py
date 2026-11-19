"""Whose GitHub token this is."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.github_call import github_call

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn


def github_user_login(sign_in: GithubSignIn, token: str) -> str | None:
    """The login of the token's user, else None."""
    reply = github_call(f"{sign_in.api_url}/user", token)
    login = reply.body.get("login") if isinstance(reply.body, dict) else None
    ok = reply.status == HTTPStatus.OK and isinstance(login, str) and login
    return login if ok else None
