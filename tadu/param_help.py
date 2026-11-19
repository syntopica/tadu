"""What the command line and a tool say about an argument."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.param import Param


def param_help(param: Param) -> str:
    """Its help, led by the one backlog format that takes it, such as `format 2: type slug`."""
    return f"format {param.format}: {param.help}" if param.format else param.help
