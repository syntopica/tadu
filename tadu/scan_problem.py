"""A repository that could not be scanned."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScanProblem:
    """The repository key and why its backlog was skipped."""

    repository: str
    message: str
