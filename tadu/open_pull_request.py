"""Open a pull request with a proposal's changes on a new branch."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.create_pull import create_pull
from tadu.proposal_field import proposal_field

if TYPE_CHECKING:
    from tadu.proposal_request import ProposalRequest
    from tadu.repository_api import RepositoryApi


def open_pull_request(api: RepositoryApi, default: str, request: ProposalRequest) -> str:
    """The address of a pull request from a new branch holding one commit of the changes.

    The branch (`tadu/<operation>-<random>`) is cut from the head of `default`, which is
    never written. The changes are first compared with the files GitHub holds there: any that
    differ raise ProposalError with status CONFLICT, and nothing is created.
    """
    return proposal_field(create_pull(api, default, request), "html_url")
