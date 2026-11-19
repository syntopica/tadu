"""Run a command's function, importing its module only now."""

from __future__ import annotations

from importlib import import_module


def run_command(name: str, *arguments: object, **options: object) -> int:
    """Call the function `name` of the module `tadu.<name>` and return its exit status.

    Each tadu module is named after its one function, so the name finds both; importing
    it here means a call of `tadu list` does not load the board's or the MCP server first.
    """
    function = getattr(import_module(f"tadu.{name}"), name)
    status: int = function(*arguments, **options)
    return status
