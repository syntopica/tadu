"""The board command."""

from __future__ import annotations

import secrets
import sys
from contextlib import suppress
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.allowed_hosts import allowed_hosts
from tadu.board_state import BoardState
from tadu.load_cards import load_cards
from tadu.loopback_hosts import LOOPBACK_HOSTS
from tadu.make_board_handler import make_board_handler
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse


def run_board(args: argparse.Namespace) -> int:
    """Check the workspace loads, then serve it until interrupted."""
    today = datetime.now(UTC).astimezone().date()
    try:
        load_cards((), args.workspace, args.done_days, today)
    except WorkspaceError as error:
        print(f"tadu board: {error}", file=sys.stderr)
        return 2
    try:
        server = ThreadingHTTPServer((args.host, args.port), BaseHTTPRequestHandler)
    except OSError as error:
        print(f"tadu board: cannot listen on {args.host}:{args.port}: {error}", file=sys.stderr)
        return 2
    with server:
        port = server.server_address[1]
        if args.host not in LOOPBACK_HOSTS:
            print(
                f"tadu board: warning: listening on {args.host}; only requests whose "
                f"Host header is {args.host}:{port} are served",
                file=sys.stderr,
            )
        token = secrets.token_urlsafe(32)
        hosts = allowed_hosts(args.host, port)
        state = BoardState(Path(args.workspace), args.done_days, token, hosts)
        server.RequestHandlerClass = make_board_handler(state)
        print(f"http://{args.host}:{port}/?token={token}", flush=True)
        with suppress(KeyboardInterrupt):
            server.serve_forever()
    return 0
