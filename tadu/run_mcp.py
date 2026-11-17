"""The mcp command: the backlog as tools for an agent, over stdio."""

from __future__ import annotations

import io
import sys
from typing import TYPE_CHECKING

from tadu.mcp_call import mcp_call
from tadu.mcp_scope import McpScope
from tadu.mcp_serve import mcp_serve

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable


def run_mcp(args: argparse.Namespace, main: Callable[[list[str]], int]) -> int:
    """Serve until standard input closes; `main` is the tadu command line each tool runs."""
    scope = McpScope(tuple(args.paths), args.workspace)
    source = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
    out = sys.stdout

    def write(text: str) -> None:
        out.write(text)
        out.flush()

    mcp_serve(source, write, lambda name, arguments: mcp_call(name, arguments, scope, main))
    return 0
