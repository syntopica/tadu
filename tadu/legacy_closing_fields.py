"""The closing fields a legacy item lacks, so its migrated task is valid."""

from __future__ import annotations

from datetime import UTC, datetime

LEGACY_NOTE = "legacy item migrated to format 2 without a recorded"


def legacy_closing_fields(
    state: str, day: str | None, found: dict[str, object]
) -> dict[str, object]:
    """closed, result, evidence and resolution; found holds what the item's own bullets gave.

    An open item gets none. A done or cancelled one with no closing day gets the migration day,
    and missing text says the entry came from a legacy log.
    """
    if state not in ("done", "cancelled"):
        return {"closed": None, "result": "", "evidence": [], "resolution": ""}
    closed = day or datetime.now(UTC).date().isoformat()
    if state == "cancelled":
        return {
            **found,
            "closed": closed,
            "resolution": found["resolution"] or f"{LEGACY_NOTE} resolution",
        }
    return {
        **found,
        "closed": closed,
        "result": found["result"] or found["title"],
        "evidence": found["evidence"] or [f"{LEGACY_NOTE} evidence"],
    }
