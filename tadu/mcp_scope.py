"""What a `tadu mcp` server reads: repository roots or one workspace."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class McpScope:
    """The roots (default `.`) or the workspace directory the server was started with."""

    paths: tuple[str, ...]
    workspace: str | None

    def argv(self) -> list[str]:
        """The scope as the arguments of a reading command."""
        if self.workspace is not None:
            return [f"--workspace={self.workspace}"]
        return ["--", *(self.paths or (".",))]
