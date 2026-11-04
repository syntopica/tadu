"""Write one board response."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from http.server import BaseHTTPRequestHandler


def send_board_response(
    handler: BaseHTTPRequestHandler, response: tuple[int, bytes, str], *extra: tuple[str, str]
) -> None:
    """Send status, content headers, any extra headers and, except for HEAD, the body."""
    status, body, content_type = response
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    for name, value in extra:
        handler.send_header(name, value)
    handler.end_headers()
    if handler.command != "HEAD":
        handler.wfile.write(body)
