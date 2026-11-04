"""A JSON error response."""

from __future__ import annotations

import json


def json_error(status: int, message: str) -> tuple[int, bytes, str]:
    """Status, `{"error": message}` and the JSON content type."""
    body = json.dumps({"error": message}, ensure_ascii=False).encode()
    return status, body, "application/json; charset=utf-8"
