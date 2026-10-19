"""Detect line endings a close cannot split on safely."""

from __future__ import annotations

IRREGULAR = ("\r", "\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029")


def has_irregular_newlines(text: str) -> bool:
    """True for CRLF mixed with LF, a bare CR, or any other character splitlines() breaks on."""
    lf = text.replace("\r\n", "\n")
    mixed = 0 < text.count("\r\n") < text.count("\n")
    return mixed or any(mark in lf for mark in IRREGULAR)
