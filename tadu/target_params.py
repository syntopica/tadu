"""The arguments that say which repositories an operation reads or changes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.param import Param

if TYPE_CHECKING:
    from tadu.operation import Operation

ROOTS = "repository roots (default: .)"
WORKSPACE = Param("workspace", "text", "directory holding tadu-workspace.toml", metavar="DIR")
REPOSITORY = Param(
    "repository",
    "text",
    "one repository: its workspace key, or the label its items carry (the directory name, or "
    "the full path of roots that share one); a change needs it when there are several",
    metavar="KEY",
)
WRITE = Param("write", "flag", "apply the change; without it, print what would change")


def target_params(operation: Operation) -> tuple[Param, ...]:
    """Repository roots, --workspace and --repository, and --write for a change; none for none."""
    if operation.target == "none":
        return ()
    paths = (
        Param("paths", "list", ROOTS, default=[], positional=True)
        if operation.target == "roots"
        else Param("paths", "list", ROOTS, default=[], flags=("--root",), metavar="PATH")
    )
    write = (WRITE,) if operation.writes else ()
    return (paths, WORKSPACE, REPOSITORY, *write)
