"""Open a pull request with a proposal's changes on a new branch."""

from __future__ import annotations

import secrets
from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.base_moved import base_moved
from tadu.default_head import default_head
from tadu.proposal_body import proposal_body
from tadu.proposal_error import ProposalError
from tadu.proposal_field import proposal_field
from tadu.proposal_title import proposal_title
from tadu.remote_blobs import remote_blobs
from tadu.tree_entries import tree_entries

if TYPE_CHECKING:
    from tadu.proposal_request import ProposalRequest
    from tadu.repository_api import RepositoryApi

MOVED = "the repository changed since the board last read it; refresh and try again"


def open_pull_request(api: RepositoryApi, default: str, request: ProposalRequest) -> str:
    """The address of a pull request from a new branch holding one commit of the changes.

    The branch (`tadu/<operation>-<random>`) is cut from the head of `default`, which is
    never written. The changes are first compared with the files GitHub holds there: any that
    differ raise ProposalError with status CONFLICT, and nothing is created.
    """
    title = proposal_title(request.operation, request.arguments)
    commit, tree = default_head(api, default)
    if base_moved(request.changes, remote_blobs(api, tree)):
        raise ProposalError(MOVED, HTTPStatus.CONFLICT)
    made = api.post("/git/trees", {"base_tree": tree, "tree": tree_entries(request.changes)})
    parents = [commit]
    child = api.post(
        "/git/commits", {"message": title, "tree": proposal_field(made, "sha"), "parents": parents}
    )
    branch = f"tadu/{request.operation}-{secrets.token_hex(4)}"
    api.post("/git/refs", {"ref": f"refs/heads/{branch}", "sha": proposal_field(child, "sha")})
    pull = api.post(
        "/pulls",
        {
            "title": title,
            "head": branch,
            "base": default,
            "body": proposal_body(request, issue=False),
        },
    )
    return proposal_field(pull, "html_url")
