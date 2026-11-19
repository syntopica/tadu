"""The tadu command line a tool call runs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.tool_params import tool_params

if TYPE_CHECKING:
    from tadu.operation import Operation
    from tadu.scope import Scope


def operation_argv(operation: Operation, arguments: dict[str, object], scope: Scope) -> list[str]:
    """Options as `--flag=value`, so no value reads as a flag; positionals after `--`.

    A true flag is bare and a false one left out; a list repeats its flag. The server's scope
    follows: its workspace, else its roots (as `--root` where the operation takes them so). A
    change writes unless `preview` is true.
    """
    options: list[str] = []
    positionals: list[str] = []
    for param in tool_params(operation):
        value = arguments.get(param.name)
        if value is None or value is False or param.name == "preview":
            continue
        if param.positional:
            positionals += (
                [str(item) for item in value] if isinstance(value, list) else [str(value)]
            )
        elif value is True:
            options.append(param.flag)
        else:
            options += [
                f"{param.flag}={item}" for item in (value if isinstance(value, list) else [value])
            ]
    if operation.writes and arguments.get("preview") is not True:
        options.append("--write")
    paths = list(scope.paths)
    if scope.workspace is not None:
        options.append(f"--workspace={scope.workspace}")
    if operation.target == "root":
        options += [f"--root={path}" for path in paths]
        paths = []
    return [operation.name, "--no-config", *options, "--", *positionals, *paths]
