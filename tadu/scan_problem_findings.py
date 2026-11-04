"""W003 findings for repositories that could not be scanned."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding

if TYPE_CHECKING:
    from tadu.scan_problem import ScanProblem


def scan_problem_findings(problems: tuple[ScanProblem, ...]) -> tuple[Finding, ...]:
    """One warning per skipped repository."""
    return tuple(Finding("W003", "warning", p.repository, 0, p.message) for p in problems)
