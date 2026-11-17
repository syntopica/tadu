"""The tadu command line a tool call runs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.mcp_options import mcp_options
from tadu.mcp_repository_root import mcp_repository_root

if TYPE_CHECKING:
    from tadu.mcp_scope import McpScope


def mcp_argv(name: str, arguments: dict[str, object], scope: McpScope) -> list[str]:
    """Options first, positionals after `--`.

    A writing tool runs with --write on its one repository; WorkspaceError when that
    repository cannot be told.
    """
    options = mcp_options(arguments)
    if name in ("add", "mark", "close"):
        repository = arguments.get("repository")
        root = mcp_repository_root(scope, repository if isinstance(repository, str) else None)
        return [name, *options, "--write", "--", root]
    if name == "show" and scope.workspace is None:
        return ["show", "--", str(arguments["key"]), *(scope.paths or (".",))]
    if name == "show":
        return ["show", f"--workspace={scope.workspace}", "--", str(arguments["key"])]
    return [name, *options, *scope.argv()]
