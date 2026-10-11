"""The line ending a text mostly uses."""

from __future__ import annotations


def dominant_newline(text: str) -> str:
    """CRLF when it outnumbers bare LF, otherwise LF."""
    crlf = text.count("\r\n")
    return "\r\n" if crlf > text.count("\n") - crlf else "\n"
