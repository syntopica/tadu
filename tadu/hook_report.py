"""The context line a Claude Code hook adds after a backlog change."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.doctor_checks import DOCTOR_CHECKS
from tadu.finding import Finding
from tadu.format_finding import format_finding
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path


def hook_report(root: Path, limit: int) -> str | None:
    """The doctor errors for `root` as text for the agent, or None when there are none."""
    errors: list[Finding] = []
    for check in DOCTOR_CHECKS:
        try:
            findings = check(root)
        except UnreadableFileError as error:
            findings = (Finding("E001", "error", str(error.path), 0, str(error)),)
        errors.extend(finding for finding in findings if finding.severity == "error")
    if not errors:
        return None
    lines = [format_finding(finding, as_json=False) for finding in errors[:limit]]
    more = [f"... and {len(errors) - limit} more"] if len(errors) > limit else []
    head = (
        f"tadu doctor {root} reports {len(errors)} error(s) after this change. If the paired "
        "TODO.md / TODO_LOG.md edit is still to come, recheck after it; otherwise fix them "
        "before committing (`tadu close` moves an item and writes its log entry):"
    )
    return "\n".join([head, *lines, *more])
