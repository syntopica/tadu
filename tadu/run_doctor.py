"""The doctor command."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tadu.check_workspace_items import check_workspace_items
from tadu.doctor_checks import DOCTOR_CHECKS
from tadu.finding import Finding
from tadu.format_finding import format_finding
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from datetime import date


def run_doctor(
    paths: tuple[str, ...],
    *,
    as_json: bool,
    workspace: str | None = None,
    today: date | None = None,
) -> int:
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
    if workspace is not None and today is not None:
        for finding in check_workspace_items(Path(workspace), today):
            print(format_finding(finding, as_json=as_json))
            failed = failed or finding.severity == "error"
    return 1 if failed else 0
