"""One tadu operation: a command line, an MCP tool and a board call, declared once."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.param import Param


@dataclass(frozen=True)
class Operation:
    """An operation: its name, help, arguments, the access it needs and what it reads.

    `access` is read, write, admin (rewrites many files) or local (a server or a hook, never a
    tool). `target` is roots (repository paths as positionals), root (paths as `--root`) or
    none; with either of the first two it also takes `--workspace` and `--repository`, and a
    write or admin operation `--write`. `describe` is what an agent is told (default: help).
    """

    name: str
    help: str
    params: tuple[Param, ...]
    access: str = "read"
    target: str = "roots"
    describe: str = ""

    @property
    def writes(self) -> bool:
        """Whether it changes files: its access is write or admin."""
        return self.access in ("write", "admin")
