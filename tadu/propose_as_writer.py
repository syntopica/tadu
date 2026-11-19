"""Apply a change by someone who may push, the way the repository's `proposals` says."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.open_pull_request import open_pull_request
from tadu.proposal_review import REVIEW
from tadu.propose_direct import propose_direct
from tadu.propose_merge import propose_merge

if TYPE_CHECKING:
    from tadu.proposal_request import ProposalRequest
    from tadu.repository_api import RepositoryApi


def propose_as_writer(api: RepositoryApi, default: str, site: str, request: ProposalRequest) -> str:
    """What to tell the person: the pull request, merge or commit the request's mode made.

    `site` is the repository's web address. ProposalError as the steps raise it.
    """
    if request.mode == "merge":
        return propose_merge(api, default, request)
    if request.mode == "direct":
        return propose_direct(api, default, site, request)
    return f"proposed: {open_pull_request(api, default, request)} ({REVIEW})"
