"""A JSON response of the board."""

from __future__ import annotations

import json


def json_response(status: int, payload: object) -> tuple[int, bytes, str]:
    """Status, the payload as UTF-8 JSON, and the JSON content type."""
    body = json.dumps(payload, ensure_ascii=False).encode()
    return status, body, "application/json; charset=utf-8"
