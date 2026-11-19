"""Apply a pusher's change as a commit on the default branch."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.commit_to_default import commit_to_default
from tadu.open_pull_request import open_pull_request
from tadu.proposal_error import ProposalError
from tadu.proposal_review import REVIEW

if TYPE_CHECKING:
    from tadu.proposal_request import ProposalRequest
    from tadu.repository_api import RepositoryApi


def propose_direct(api: RepositoryApi, default: str, site: str, request: ProposalRequest) -> str:
    """What to tell the person; `site` is the repository's web address.

    A commit GitHub refuses (a protected branch) falls back to a pull request for review. A
    CONFLICT (the repository moved) is raised, not retried.
    """
    try:
        sha = commit_to_default(api, default, request)
    except ProposalError as error:
        if error.status == HTTPStatus.CONFLICT:
            raise
        url = open_pull_request(api, default, request)
        return f"proposed: {url} (GitHub would not take a commit on {default}; {REVIEW})"
    return f"committed: {site}/commit/{sha} (the card changes once the checkout is pulled)"
