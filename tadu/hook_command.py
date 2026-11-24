"""Run the Claude Code hook over standard input."""

from __future__ import annotations

import sys

from tadu.run_codex_hook import run_codex_hook
from tadu.run_hook import run_hook


def hook_command(agent: str = "claude") -> int:
    """Print the hook's JSON when it has something to say; always exit 0, so it never blocks.

    The bytes are decoded leniently: a stray byte must not turn into a traceback.
    """
    runner = run_codex_hook if agent == "codex" else run_hook
    output = runner(sys.stdin.buffer.read().decode("utf-8", "replace"))
    if output is not None:
        print(output)
    return 0
