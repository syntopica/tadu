"""Tell GitHub to revoke a person's token when their session ends on purpose."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import quote

import requests

from tadu.github_session import GithubSession

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn

TIMEOUT_SECONDS = 5


def revoke_github_token(sign_in: GithubSignIn, token: str) -> bool:
    """DELETE /applications/{client_id}/token; True when GitHub revoked it (204).

    The board forgets a session's token when it ends anyway, but GitHub would still take
    it: for 8 hours from a GitHub App, for ever from an OAuth App, whose `repo` scope can
    write. Revoked, the token is worthless wherever a copy of it may be. Best effort:
    a GitHub that cannot be reached does not stop a sign-out. The app authenticates with
    its client ID and secret, as explicit credentials (never ~/.netrc), and the request
    stays on GitHub's origin (GithubSession).
    """
    url = f"{sign_in.api_url}/applications/{quote(sign_in.client_id, safe='')}/token"
    try:
        with GithubSession() as session:
            answer = session.delete(
                url,
                json={"access_token": token},
                auth=(sign_in.client_id, sign_in.client_secret),
                headers={"Accept": "application/vnd.github+json"},
                timeout=TIMEOUT_SECONDS,
                allow_redirects=False,
            )
    except requests.RequestException:
        return False
    return answer.status_code == HTTPStatus.NO_CONTENT
