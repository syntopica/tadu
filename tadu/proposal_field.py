"""A text GitHub's answer holds."""

from __future__ import annotations

from tadu.proposal_error import ProposalError


def proposal_field(answer: dict[str, object], key: str) -> str:
    """`answer[key]` when it is a text; ProposalError when GitHub's answer lacks it."""
    value = answer.get(key)
    if not isinstance(value, str):
        msg = f"GitHub's answer did not hold the {key} expected"
        raise ProposalError(msg)
    return value
