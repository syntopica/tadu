"""One problem found in an item field."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldProblem:
    """A field problem at a 0-based line index of the file."""

    line: int
    message: str
