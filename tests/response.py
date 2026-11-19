import http.client
from dataclasses import dataclass


@dataclass(frozen=True)
class Response:
    """What a board answered: status, headers and body."""

    status: int
    headers: http.client.HTTPMessage
    body: bytes
