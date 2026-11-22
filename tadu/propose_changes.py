"""Propose a change to GitHub as the person who asked."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.open_issue import open_issue
from tadu.proposal_error import ProposalError
from tadu.proposal_field import proposal_field
from tadu.propose_as_writer import propose_as_writer
from tadu.repository_api import RepositoryApi

if TYPE_CHECKING:
    from tadu.github_sign_in import GithubSignIn
    from tadu.proposal_request import ProposalRequest


def propose_changes(
    sign_in: GithubSignIn, token: str | None, name: str, request: ProposalRequest
) -> str:
    """What to tell the person: what the request's mode made if they may push to `name`, else an issue.

    The mode is `pr`, `merge` or `direct` (see propose_as_writer), on the request's branch,
    else the repository's default branch.

    Everything goes to GitHub with their token, so GitHub holds them to their rights and
    names them the author. ProposalError when nothing could be made; SignedOutError when
    GitHub refuses the token. Nothing is sent without a token.
    """
    if token is None:
        msg = "GitHub could not be reached; try again"
        raise ProposalError(msg)
    api = RepositoryApi(sign_in.api_url, token, name)
    repository = api.get("")
    permissions = repository.get("permissions")
    if isinstance(permissions, dict) and permissions.get("push") is True:
        default = request.branch or proposal_field(repository, "default_branch")
        site = proposal_field(repository, "html_url")
        return propose_as_writer(api, default, site, request)
    url = open_issue(api, request)
    return f"proposed: {url} (an issue, as you may not push; the card changes once it is done)"
