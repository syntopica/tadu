"""Checks for the conversation coverage index."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.check_index_record_fields import check_index_record_fields
from tadu.finding import Finding
from tadu.read_text_exact import read_text_exact

if TYPE_CHECKING:
    from pathlib import Path


def check_history_index(root: Path) -> tuple[Finding, ...]:
    """Report malformed, mistyped, unknown-status, duplicate and out-of-order records."""
    path = root / "TODO_HISTORY_INDEX.jsonl"
    if not path.is_file():
        return ()
    findings: list[Finding] = []
    seen: set[tuple[str, str]] = set()
    previous: tuple[str, str] | None = None
    unsorted_reported = False
    for number, line in enumerate(read_text_exact(path).splitlines(), start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            record = None
        if not isinstance(record, dict):
            findings.append(Finding("H001", "error", str(path), number, "not a JSON object"))
            continue
        fields = check_index_record_fields(record, str(path), number)
        findings.extend(fields)
        if any(finding.code in ("H002", "H006") for finding in fields):
            continue
        key = (record["source"], record["conversation_id"])
        if key in seen:
            findings.append(
                Finding("H004", "error", str(path), number, "duplicate source + conversation_id")
            )
        seen.add(key)
        if previous is not None and key < previous and not unsorted_reported:
            message = "records are not sorted by source and conversation_id"
            findings.append(Finding("H005", "warning", str(path), number, message))
            unsorted_reported = True
        previous = key
    return tuple(findings)
