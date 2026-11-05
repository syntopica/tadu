"""The repositories an MCP server reads."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class McpScope:
    """Repository roots or a workspace, fixed when the server starts."""

    paths: tuple[str, ...]
    workspace: str | None
    done_days: int
