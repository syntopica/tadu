"""Checks for the conversation coverage index."""

from __future__ import annotations

import json
from pathlib import Path

from tadu.finding import Finding
from tadu.index_required_keys import INDEX_REQUIRED_KEYS
from tadu.review_statuses import REVIEW_STATUSES


def check_history_index(root: Path) -> tuple[Finding, ...]:
    """Report malformed, incomplete, unknown-status and duplicate records."""
    path = root / "TODO_HISTORY_INDEX.jsonl"
    if not path.is_file():
        return ()
    findings: list[Finding] = []
    seen: set[tuple[str, str]] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            record = None
        if not isinstance(record, dict):
            findings.append(Finding("H001", "error", str(path), number, "not a JSON object"))
            continue
        missing = [key for key in INDEX_REQUIRED_KEYS if key not in record]
        if missing:
            findings.append(
                Finding("H002", "error", str(path), number, f"missing {', '.join(missing)}")
            )
            continue
        status = record["review_status"]
        if not isinstance(status, str) or status not in REVIEW_STATUSES:
            findings.append(
                Finding("H003", "error", str(path), number, f"unknown status {status!r}")
            )
        key = (str(record["source"]), str(record["conversation_id"]))
        if key in seen:
            findings.append(
                Finding("H004", "error", str(path), number, "duplicate source + conversation_id")
            )
        seen.add(key)
    return tuple(findings)
