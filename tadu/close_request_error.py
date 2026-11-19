"""Validate the free-text arguments of a close request."""

from __future__ import annotations

from tadu.text_problem import text_problem


def close_request_error(
    match: str, proof: str | None, fields: tuple[str | None, ...]
) -> str | None:
    """Why the request cannot run, or None: empty values and line breaks are refused."""
    if proof is None or not proof.strip():
        return "give exactly one non-empty --evidence or --resolution"
    return text_problem(value for value in (match, *fields) if value is not None)
