"""The newest commit of a repository's default branch."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from tadu.proposal_error import ProposalError

if TYPE_CHECKING:
    from tadu.repository_api import RepositoryApi


def default_head(api: RepositoryApi, branch: str) -> tuple[str, str]:
    """The commit at the head of `branch` and the tree of that commit.

    ProposalError when GitHub's answers do not name them.
    """
    ref = api.get(f"/git/ref/heads/{quote(branch)}")
    target = ref.get("object")
    commit = target.get("sha") if isinstance(target, dict) else None
    if not isinstance(commit, str):
        msg = "GitHub did not say where the default branch is"
        raise ProposalError(msg)
    tree = api.get(f"/git/commits/{commit}").get("tree")
    sha = tree.get("sha") if isinstance(tree, dict) else None
    if not isinstance(sha, str):
        msg = "GitHub did not say what the default branch holds"
        raise ProposalError(msg)
    return commit, sha
