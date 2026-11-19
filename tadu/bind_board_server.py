"""Bind the board's listening socket."""

from __future__ import annotations

import sys
from http.server import BaseHTTPRequestHandler

from tadu.board_http_server import BoardHttpServer


def bind_board_server(host: str, port: int, *, fallback: bool) -> BoardHttpServer:
    """Bind host:port; with `fallback`, a busy port gives way to any free one. OSError escapes."""
    try:
        return BoardHttpServer((host, port), BaseHTTPRequestHandler)
    except OSError:
        if not fallback:
            raise
    print(f"tadu board: port {port} is busy; using any free port", file=sys.stderr)
    return BoardHttpServer((host, 0), BaseHTTPRequestHandler)
