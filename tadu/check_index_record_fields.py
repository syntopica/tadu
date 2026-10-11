"""Field-level checks for one history index record."""

from __future__ import annotations

from tadu.finding import Finding
from tadu.index_required_keys import INDEX_REQUIRED_KEYS
from tadu.review_statuses import REVIEW_STATUSES


def check_index_record_fields(
    record: dict[str, object], path: str, number: int
) -> tuple[Finding, ...]:
    """Report missing keys, wrongly typed fields and an unknown review status."""
    missing = [key for key in INDEX_REQUIRED_KEYS if key not in record]
    if missing:
        return (Finding("H002", "error", path, number, f"missing {', '.join(missing)}"),)
    findings: list[Finding] = []
    wrong = [
        key
        for key in ("source", "conversation_id")
        if not (isinstance(record[key], str) and str(record[key]).strip())
    ]
    version = record["review_version"]
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        wrong.append("review_version")
    status = record["review_status"]
    if not isinstance(status, str):
        wrong.append("review_status")
    if wrong:
        findings.append(
            Finding("H006", "error", path, number, f"wrong field type: {', '.join(wrong)}")
        )
    if isinstance(status, str) and status not in REVIEW_STATUSES:
        findings.append(Finding("H003", "error", path, number, f"unknown status {status!r}"))
    return tuple(findings)
