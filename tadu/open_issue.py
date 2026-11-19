"""Open an issue that asks for a change."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.proposal_body import proposal_body
from tadu.proposal_field import proposal_field
from tadu.proposal_title import proposal_title

if TYPE_CHECKING:
    from tadu.proposal_request import ProposalRequest
    from tadu.repository_api import RepositoryApi


def open_issue(api: RepositoryApi, request: ProposalRequest) -> str:
    """The address of a new issue holding the request, its arguments and the diff of the changes."""
    title = proposal_title(request.operation, request.arguments)
    issue = api.post("/issues", {"title": title, "body": proposal_body(request, issue=True)})
    return proposal_field(issue, "html_url")
