"""The board columns an MCP filter accepts."""

from __future__ import annotations

from typing import Literal

McpColumn = Literal["backlog", "ready", "in_progress", "blocked", "done", "cancelled"]
