"""The arguments an operation takes as a tool, of MCP or of the board."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.param import Param
from tadu.target_params import REPOSITORY

if TYPE_CHECKING:
    from tadu.operation import Operation

PREVIEW = Param("preview", "flag", "only say what would change; write nothing")


def tool_params(operation: Operation) -> tuple[Param, ...]:
    """Its own arguments, `repository`, and `preview` for a change.

    The server's scope stands for the roots and the workspace; a change writes unless previewed.
    """
    return (*operation.params, REPOSITORY, *((PREVIEW,) if operation.writes else ()))
