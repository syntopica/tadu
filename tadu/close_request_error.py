"""Validate the free-text arguments of a close request."""

from __future__ import annotations


def close_request_error(
    match: str, proof: str | None, fields: tuple[str | None, ...]
) -> str | None:
    """Why the request cannot run, or None: empty values and line breaks are refused."""
    if proof is None or not proof.strip():
        return "give exactly one non-empty --evidence or --resolution"
    values = [value for value in (match, *fields) if value is not None]
    if any(not value.strip() for value in values):
        return "arguments must not be blank"
    if any(len(f"{value}x".splitlines()) > 1 for value in values):
        return "arguments must be single lines"
    return None
