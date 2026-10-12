"""The doctor command."""

from __future__ import annotations

from pathlib import Path

from tadu.doctor_checks import DOCTOR_CHECKS
from tadu.finding import Finding
from tadu.format_finding import format_finding
from tadu.unreadable_file_error import UnreadableFileError


def run_doctor(paths: tuple[str, ...], *, as_json: bool) -> int:
    """Print every finding for every root; exit 1 when any is an error."""
    failed = False
    for raw in paths:
        root = Path(raw)
        for check in DOCTOR_CHECKS:
            try:
                findings = check(root)
            except UnreadableFileError as error:
                findings = (Finding("E001", "error", str(error.path), 0, str(error)),)
            for finding in findings:
                print(format_finding(finding, as_json=as_json))
                failed = failed or finding.severity == "error"
    return 1 if failed else 0
