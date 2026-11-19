"""The doctor command."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tadu.check_workspace_items import check_workspace_items
from tadu.format_finding import format_finding
from tadu.root_findings import root_findings

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
    findings = [finding for raw in paths for finding in root_findings(Path(raw))]
    if workspace is not None and today is not None:
        findings += check_workspace_items(Path(workspace), today)
    for finding in findings:
        print(format_finding(finding, as_json=as_json))
        failed = failed or finding.severity == "error"
    return 1 if failed else 0
