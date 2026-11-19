"""Run one MCP tool call."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.mcp_arguments_error import mcp_arguments_error
from tadu.mcp_argv import mcp_argv
from tadu.mcp_tools import MCP_TOOLS
from tadu.run_captured import run_captured
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from collections.abc import Callable

    from tadu.mcp_scope import McpScope


def mcp_call(
    name: str, arguments: object, scope: McpScope, main: Callable[[list[str]], int]
) -> dict[str, object]:
    """The `tools/call` result: the command's output as text, an error when it fails.

    The caller has checked that the tool exists. The command reads no config file: a
    tool does what its schema says, whatever defaults a person set for their own use.
    """
    problem = mcp_arguments_error(MCP_TOOLS[name]["inputSchema"], arguments)  # type: ignore[arg-type]
    if problem is None:
        try:
            code, text = run_captured(main, ["--no-config", *mcp_argv(name, arguments, scope)])  # type: ignore[arg-type]
        except WorkspaceError as error:
            code, text = 2, str(error)
    else:
        code, text = 2, problem
    return {
        "content": [{"type": "text", "text": text.strip() or "Nothing found."}],
        "isError": code != 0,
    }
