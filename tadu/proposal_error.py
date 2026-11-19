"""A proposal that cannot be made."""

from __future__ import annotations

from http import HTTPStatus


class ProposalError(Exception):
    """Why a change cannot be proposed; the message is safe to show the person.

    `status` is the HTTP status of the answer: 200 for a refusal the page shows as an exit
    status 2 (the usual case), CONFLICT for a repository that moved since the board read it.
    """

    def __init__(self, message: str, status: int = HTTPStatus.OK) -> None:
        super().__init__(message)
        self.status = status
