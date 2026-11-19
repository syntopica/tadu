"""The files of a repository's tree, as GitHub holds them."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.proposal_error import ProposalError

if TYPE_CHECKING:
    from tadu.repository_api import RepositoryApi


def remote_blobs(api: RepositoryApi, tree: str) -> dict[str, str]:
    """Path to blob SHA of every file in the tree.

    ProposalError when GitHub cuts the listing short (a repository too large to list whole):
    what a file held could then not be told.
    """
    listing = api.get(f"/git/trees/{tree}?recursive=1")
    entries = listing.get("tree")
    if listing.get("truncated") is not False or not isinstance(entries, list):
        msg = "the repository is too large to compare with the board's copy"
        raise ProposalError(msg)
    # keys: a tree lists each path once.
    return {
        str(entry["path"]): str(entry["sha"])
        for entry in entries
        if isinstance(entry, dict) and entry.get("type") == "blob"
    }
