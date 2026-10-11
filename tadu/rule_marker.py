"""One rule marker line found in an instruction file."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuleMarker:
    """A marker of `kind` "open" or "close"; the span covers its line and line ending."""

    kind: str
    start: int
    end: int
    version: int
