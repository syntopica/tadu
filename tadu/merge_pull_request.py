"""Open a pull request with a proposal's changes and merge it at once."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.create_pull import create_pull
from tadu.proposal_error import ProposalError
from tadu.proposal_field import proposal_field

if TYPE_CHECKING:
    from tadu.proposal_request import ProposalRequest
    from tadu.repository_api import RepositoryApi


def merge_pull_request(
    api: RepositoryApi, default: str, request: ProposalRequest
) -> tuple[str, bool]:
    """The address of the pull request, and whether it was merged (squashed) into `default`.

    A merge GitHub refuses (a required review, a check, a protected branch) leaves the pull
    request open for review. The pull request's own errors are raised as create_pull raises them.
    """
    pull = create_pull(api, default, request)
    number = pull.get("number")
    try:
        api.put(f"/pulls/{number}/merge", {"merge_method": "squash"})
    except ProposalError:
        return proposal_field(pull, "html_url"), False
    return proposal_field(pull, "html_url"), True
