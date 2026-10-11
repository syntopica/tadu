"""One conformance finding."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    """A rule violation at a file and line; severity is "error" or "warning"."""

    code: str
    severity: str
    path: str
    line: int
    message: str
