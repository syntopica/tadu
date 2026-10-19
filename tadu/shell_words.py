"""Split a shell command into words, the way the shell would, without running it."""

from __future__ import annotations

import shlex


def shell_words(command: str) -> list[str]:
    """The command's words with quotes resolved; whitespace words if the quoting is unbalanced."""
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()
