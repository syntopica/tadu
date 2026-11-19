"""A JSON error response."""

from __future__ import annotations

from tadu.json_response import json_response


def json_error(status: int, message: str) -> tuple[int, bytes, str]:
    """Status, `{"error": message}` and the JSON content type."""
    return json_response(status, {"error": message})
