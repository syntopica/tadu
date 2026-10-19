"""Run the Claude Code hook over standard input."""

from __future__ import annotations

import sys

from tadu.run_hook import run_hook


def hook_command() -> int:
    """Print the hook's JSON when it has something to say; always exit 0, so it never blocks.

    The bytes are decoded leniently: a stray byte must not turn into a traceback.
    """
    output = run_hook(sys.stdin.buffer.read().decode("utf-8", "replace"))
    if output is not None:
        print(output)
    return 0
