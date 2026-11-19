"""Commit a proposal's changes straight to the default branch."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from tadu.create_commit import create_commit

if TYPE_CHECKING:
    from tadu.proposal_request import ProposalRequest
    from tadu.repository_api import RepositoryApi


def commit_to_default(api: RepositoryApi, default: str, request: ProposalRequest) -> str:
    """The sha of the commit that now is the head of `default`.

    The branch moves only forward (no force), so a push that landed meanwhile, or a branch
    GitHub protects, raises ProposalError; so does a change on files GitHub no longer holds as
    the change started (create_commit).
    """
    commit = create_commit(api, default, request)
    api.patch(f"/git/refs/heads/{quote(default)}", {"sha": commit, "force": False})
    return commit
