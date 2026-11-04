"""Warnings for malformed or repeated item fields."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding
from tadu.id_line_offset import id_line_offset
from tadu.misplaced_field_findings import misplaced_field_findings
from tadu.read_open_items import read_open_items
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path


def check_item_fields(root: Path) -> tuple[Finding, ...]:
    """Report field problems and repeated IDs; an unreadable TODO.md is E001's to report."""
    path = root / "TODO.md"
    if not path.is_file():
        return ()
    try:
        items = read_open_items(root, ".", "")
    except UnreadableFileError:
        return ()
    findings: list[Finding] = []
    first_line: dict[str, int] = {}
    for item in items:
        findings.extend(
            Finding("F001", "warning", str(path), problem.line + 1, problem.message)
            for problem in item.problems
        )
        findings.extend(misplaced_field_findings(str(path), item))
        uid = item.fields.id
        if uid is None:
            continue
        if uid not in first_line:
            first_line[uid] = item.line
            continue
        offset = id_line_offset(item.text, uid)
        message = f"ID {uid} is also used at line {first_line[uid]}"
        findings.append(Finding("F002", "warning", str(path), item.line + offset, message))
    return tuple(findings)
