"""Report repositories that could not be scanned."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.scan_problem import ScanProblem


def print_problems(command: str, problems: tuple[ScanProblem, ...]) -> None:
    """Write each problem to stderr as `tadu <command>: <repository>: <message>`."""
    for problem in problems:
        print(f"tadu {command}: {problem.repository}: {problem.message}", file=sys.stderr)
