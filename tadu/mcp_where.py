"""The `where` argument of the list_items MCP tool."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date  # noqa: TC003
from typing import ClassVar

from pydantic import ConfigDict

from tadu.mcp_column import McpColumn  # noqa: TC001
from tadu.mcp_priority import McpPriority  # noqa: TC001


@dataclass(frozen=True)
class McpWhere:
    """Optional criteria; every one that is set must hold.

    Unknown fields and values outside the CLI's choices are rejected, so a malformed filter
    fails instead of matching everything or nothing. Pydantic reads the annotations at
    runtime, so their types are imported at runtime.
    """

    __pydantic_config__: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

    project: str | None = None
    org: str | None = None
    role: str | None = None
    assignee: str | None = None
    column: McpColumn | None = None
    priority: McpPriority | None = None
    label: str | None = None
    due_before: date | None = None
    include_cancelled: bool = False
