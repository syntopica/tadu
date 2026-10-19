"""Run the Claude Code hook over standard input."""

from __future__ import annotations

import sys

from tadu.run_hook import run_hook


def hook_command() -> int:
    """Print the hook's JSON when it has something to say; always exit 0, so it never blocks."""
    output = run_hook(sys.stdin.read())
    if output is not None:
        print(output)
    return 0
