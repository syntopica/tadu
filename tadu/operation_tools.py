"""The tools a server offers at an access level."""

from __future__ import annotations

from functools import cache

from tadu.access_allows import access_allows
from tadu.operation_tool import operation_tool
from tadu.operations import OPERATIONS


@cache
def operation_tools(allow: str) -> dict[str, dict[str, object]]:
    """Every operation `allow` permits as a tool, by name; never a server or the hook.

    Built once per level; callers read it and never change it.
    """
    return {
        name: operation_tool(operation)
        for name, operation in OPERATIONS.items()
        if operation.access != "local" and access_allows(allow, operation.access)
    }
