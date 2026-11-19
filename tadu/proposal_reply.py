"""What GitHub answered to a step of a proposal."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.proposal_error import ProposalError
from tadu.signed_out_error import SignedOutError

if TYPE_CHECKING:
    from tadu.github_reply import GithubReply


def proposal_reply(reply: GithubReply) -> dict[str, object]:
    """The JSON object of a successful answer.

    Raise SignedOutError when GitHub refuses the token; ProposalError, without the answer's
    own text, for anything else that is not a success.
    """
    if reply.status == HTTPStatus.UNAUTHORIZED:
        raise SignedOutError
    if reply.status == 0:
        msg = "GitHub could not be reached; try again"
        raise ProposalError(msg)
    if not 200 <= reply.status < 300 or not isinstance(reply.body, dict):  # noqa: PLR2004
        msg = f"GitHub refused the step (status {reply.status}); your rights may not allow it"
        raise ProposalError(msg)
    return reply.body
