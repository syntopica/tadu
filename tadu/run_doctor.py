"""The doctor command."""

from __future__ import annotations

from pathlib import Path

from tadu.doctor_checks import DOCTOR_CHECKS
from tadu.format_finding import format_finding


def run_doctor(paths: tuple[str, ...], as_json: bool) -> int:
    """Print every finding for every root; exit 1 when any is an error."""
    failed = False
    for raw in paths:
        root = Path(raw)
        for check in DOCTOR_CHECKS:
            for finding in check(root):
                print(format_finding(finding, as_json))
                failed = failed or finding.severity == "error"
    return 1 if failed else 0
