"""The board command."""

from __future__ import annotations

import sys
from contextlib import suppress
from typing import TYPE_CHECKING

from tadu.bind_board_server import bind_board_server
from tadu.board_preflight import board_preflight
from tadu.board_warnings import board_warnings
from tadu.make_board_handler import make_board_handler
from tadu.serving_board_state import serving_board_state
from tadu.workspace_port import workspace_port

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable


def run_board(args: argparse.Namespace, main: Callable[[list[str]], int]) -> int:
    """Check the workspace loads (and the GitHub sign-in is ready), then serve until interrupted.

    The page may do what --allow permits; its tool calls run `main`, the tadu command line.
    """
    team, error = board_preflight(args)
    if error is not None:
        print(f"tadu board: {error}", file=sys.stderr)
        return 2
    port = workspace_port(args.workspace) if args.port is None else args.port
    try:
        server = bind_board_server(args.host, port, fallback=args.port is None)
    except OSError as error:
        print(f"tadu board: cannot listen on {args.host}:{port}: {error}", file=sys.stderr)
        return 2
    with server:
        port = server.server_address[1]
        state = serving_board_state(args, port, main, team(port) if team is not None else None)
        for warning in board_warnings(args, state, port):
            print(f"tadu board: warning: {warning}", file=sys.stderr)
        server.RequestHandlerClass = make_board_handler(state)
        if state.github is None:
            print(f"http://{args.host}:{port}/?token={state.token}", flush=True)
        else:
            print(f"{state.github.public_url}/", flush=True)
        with suppress(KeyboardInterrupt):
            server.serve_forever()
    return 0
