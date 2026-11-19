"""Make a pull request of a proposal's changes on a new branch."""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from tadu.create_commit import create_commit
from tadu.proposal_body import proposal_body
from tadu.proposal_title import proposal_title

if TYPE_CHECKING:
    from tadu.proposal_request import ProposalRequest
    from tadu.repository_api import RepositoryApi


def create_pull(api: RepositoryApi, default: str, request: ProposalRequest) -> dict[str, object]:
    """GitHub's answer for a pull request from a new branch `tadu/<operation>-<random>`.

    The branch holds one commit of the changes (see create_commit) cut from the head of
    `default`, which is never written. ProposalError as create_commit raises it.
    """
    commit = create_commit(api, default, request)
    branch = f"tadu/{request.operation}-{secrets.token_hex(4)}"
    api.post("/git/refs", {"ref": f"refs/heads/{branch}", "sha": commit})
    return api.post(
        "/pulls",
        {
            "title": proposal_title(request.operation, request.arguments),
            "head": branch,
            "base": default,
            "body": proposal_body(request, issue=False),
        },
    )
