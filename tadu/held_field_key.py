"""Which task key holds a format 1 field value that format 2 names differently."""

from __future__ import annotations

from tadu.field_checks import FIELD_CHECKS


def held_field_key(name: str, value: str, state: str) -> str | None:
    """The key for Queue, Estimate, Not before, Kind or Check on; None when the line stays text.

    `Queue: ready` on a pending item is `queue`; a valid `Estimate:`, `Kind:` or `Check on:`
    is `estimate`, `kind` or `check_on`; a valid `Not before:` is `defer_until`, format 2's
    "not before this day".
    """
    valid = FIELD_CHECKS[name](value) is None
    keys = {
        "Queue": "queue" if value == "ready" and state == "pending" else None,
        "Estimate": "estimate" if valid else None,
        "Not before": "defer_until" if valid else None,
        "Kind": "kind" if valid else None,
        "Check on": "check_on" if valid else None,
    }
    return keys.get(name)
