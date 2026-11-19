"""The board's HTTP server."""

from __future__ import annotations

import sys
from http.server import ThreadingHTTPServer
from typing import override


class BoardHttpServer(ThreadingHTTPServer):
    """A threading HTTP server that does not print a traceback when a client goes away.

    A browser that closes a tab mid-answer, or anyone resetting connections on purpose,
    would otherwise fill the operator's log with tracebacks; any other error still
    prints one.
    """

    @override
    def handle_error(self, request: object, client_address: object) -> None:
        """Stay quiet for a connection the client dropped; report anything else."""
        if isinstance(sys.exc_info()[1], ConnectionError):
            return
        super().handle_error(request, client_address)  # type: ignore[arg-type]
