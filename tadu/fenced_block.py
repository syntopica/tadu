"""Text in a Markdown code fence that nothing inside it can close."""

from __future__ import annotations

import re


def fenced_block(text: str, info: str = "") -> str:
    """The text in a fence longer than any run of backticks it holds."""
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}{info}\n{text.rstrip()}\n{fence}"
