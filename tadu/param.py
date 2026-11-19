"""One argument of an operation, as the command line, MCP and the board take it."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True)
class Param:
    """An argument: its name, kind and help, declared once for every surface.

    `name` is the argparse destination and the tool property. `kind` is text, day, count,
    flag, choice, list (repeatable; an array for a tool) or words (positional, one or more).
    `flags` are the command-line spellings (default `--name-with-dashes`); `aliases` other names
    a tool call may use for it, beside those its flags spell; `exclusive` names a mutually
    exclusive group, required when its first member is; `section` a help section; `format` 1
    or 2 when only that backlog format takes it (0: both).
    """

    name: str
    kind: str
    help: str
    choices: tuple[str, ...] = ()
    default: object = None
    required: bool = False
    positional: bool = False
    flags: tuple[str, ...] = ()
    metavar: str | None = None
    exclusive: str = ""
    section: str = ""
    parse: Callable[[str], object] | None = None
    aliases: tuple[str, ...] = ()
    format: int = 0

    @property
    def flag(self) -> str:
        """Its first command-line spelling: `--name-with-dashes` unless `flags` says."""
        return self.flags[0] if self.flags else "--" + self.name.replace("_", "-")
