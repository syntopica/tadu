"""Make one commit of a proposal's changes on top of the default branch."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.base_moved import base_moved
from tadu.default_head import default_head
from tadu.proposal_error import ProposalError
from tadu.proposal_field import proposal_field
from tadu.proposal_title import proposal_title
from tadu.remote_blobs import remote_blobs
from tadu.tree_entries import tree_entries

if TYPE_CHECKING:
    from tadu.proposal_request import ProposalRequest
    from tadu.repository_api import RepositoryApi

MOVED = "the repository changed since the board last read it; refresh and try again"


def create_commit(api: RepositoryApi, default: str, request: ProposalRequest) -> str:
    """The sha of a new commit holding the changes, whose parent is the head of `default`.

    No branch points at it and `default` is not written. The changes are first compared
    with the files GitHub holds at that head: any that differ raise ProposalError with
    status CONFLICT, and nothing is created.
    """
    commit, tree = default_head(api, default)
    if base_moved(request.changes, remote_blobs(api, tree)):
        raise ProposalError(MOVED, HTTPStatus.CONFLICT)
    made = api.post("/git/trees", {"base_tree": tree, "tree": tree_entries(request.changes)})
    child = api.post(
        "/git/commits",
        {
            "message": proposal_title(request.operation, request.arguments),
            "tree": proposal_field(made, "sha"),
            "parents": [commit],
        },
    )
    return proposal_field(child, "sha")
