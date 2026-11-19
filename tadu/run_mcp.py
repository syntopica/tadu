"""The mcp command: the backlog as tools for an agent, over stdio."""

from __future__ import annotations

import io
import sys
from typing import TYPE_CHECKING

from tadu.mcp_call import mcp_call
from tadu.mcp_serve import mcp_serve
from tadu.operation_host import OperationHost
from tadu.operation_tools import operation_tools
from tadu.scope import Scope

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable


def run_mcp(args: argparse.Namespace, main: Callable[[list[str]], int]) -> int:
    """Serve the tools --allow permits until standard input closes.

    `main` is the tadu command line each tool runs.
    """
    host = OperationHost(Scope(tuple(args.paths), args.workspace), args.allow, main)
    source = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
    out = sys.stdout

    def write(text: str) -> None:
        out.write(text)
        out.flush()

    tools = operation_tools(args.allow)
    mcp_serve(source, write, tools, lambda name, arguments: mcp_call(name, arguments, host))
    return 0
