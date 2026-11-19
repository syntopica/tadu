"""Every doctor finding for one repository root."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.doctor_checks_for import doctor_checks_for
from tadu.finding import Finding
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path


def root_findings(root: Path) -> list[Finding]:
    """The findings of each check that applies to the root; a file that cannot be read is E001."""
    found: list[Finding] = []
    for check in doctor_checks_for(root):
        try:
            found.extend(check(root))
        except UnreadableFileError as error:
            found.append(Finding("E001", "error", str(error.path), 0, str(error)))
    return found
