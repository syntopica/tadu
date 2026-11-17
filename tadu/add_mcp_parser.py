"""Declare the mcp subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def add_mcp_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `mcp` to the subcommands."""
    mcp = commands.add_parser(
        "mcp",
        help="serve next, inbox, urgent, list, show, add, mark and close as MCP tools over stdio",
    )
    mcp.add_argument("paths", nargs="*", help="repository roots (default: .)")
    mcp.add_argument("--workspace", default=None, help="directory holding tadu-workspace.toml")
