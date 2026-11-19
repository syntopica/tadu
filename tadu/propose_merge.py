"""Apply a pusher's change as a pull request merged at once."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.merge_pull_request import merge_pull_request
from tadu.proposal_review import REVIEW

if TYPE_CHECKING:
    from tadu.proposal_request import ProposalRequest
    from tadu.repository_api import RepositoryApi


def propose_merge(api: RepositoryApi, default: str, request: ProposalRequest) -> str:
    """What to tell the person; a merge GitHub refuses leaves the pull request for review."""
    url, merged = merge_pull_request(api, default, request)
    if merged:
        return f"merged: {url} (the card changes once the checkout is pulled)"
    return f"proposed: {url} (GitHub would not merge it now; {REVIEW})"
