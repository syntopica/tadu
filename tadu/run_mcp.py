"""The mcp command."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.load_cards import load_cards
from tadu.mcp_scope import McpScope
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_mcp(args: argparse.Namespace, today: date) -> int:
    """Check the scope loads, then serve the read-only tools over stdio until the client leaves."""
    scope = McpScope(tuple(args.paths), args.workspace, args.done_days)
    try:
        load_cards(scope.paths, scope.workspace, scope.done_days, today)
    except WorkspaceError as error:
        print(f"tadu mcp: {error}", file=sys.stderr)
        return 2
    try:
        # Imported here so core tadu runs without the optional mcp dependency.
        from tadu.build_mcp_server import build_mcp_server  # noqa: PLC0415
    except ImportError:
        print("tadu mcp: needs the mcp extra: pip install 'tadu[mcp]'", file=sys.stderr)
        return 2
    build_mcp_server(scope).run()
    return 0
