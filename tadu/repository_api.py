"""One GitHub repository's API, with a person's token."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

from tadu.github_call import github_call
from tadu.github_send import github_send
from tadu.proposal_reply import proposal_reply


@dataclass(frozen=True)
class RepositoryApi:
    """GitHub's API for `owner/name`, called as the person the token belongs to.

    Both calls raise what proposal_reply raises. `path` is what follows the repository's
    own address: empty, or starting with `/`.
    """

    api_url: str
    token: str
    name: str

    def get(self, path: str) -> dict[str, object]:
        """The JSON object GET answers."""
        return proposal_reply(github_call(self.url(path), self.token))

    def post(self, path: str, body: dict[str, object]) -> dict[str, object]:
        """The JSON object a POST of `body` answers."""
        return proposal_reply(github_send(self.url(path), self.token, body))

    def url(self, path: str) -> str:
        """The address of `path` in the repository."""
        return f"{self.api_url}/repos/{quote(self.name)}{path}"
