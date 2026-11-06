"""Bind the board's listening socket."""

from __future__ import annotations

import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def bind_board_server(host: str, port: int, *, fallback: bool) -> ThreadingHTTPServer:
    """Bind host:port; with `fallback`, a busy port gives way to any free one. OSError escapes."""
    try:
        return ThreadingHTTPServer((host, port), BaseHTTPRequestHandler)
    except OSError:
        if not fallback:
            raise
    print(f"tadu board: port {port} is busy; using any free port", file=sys.stderr)
    return ThreadingHTTPServer((host, 0), BaseHTTPRequestHandler)
