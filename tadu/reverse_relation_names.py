"""How a relation reads from the task it points at."""

from __future__ import annotations

REVERSE_RELATION_NAMES = {
    "blocked_by": "blocks",
    "related": "related (linked from)",
    "discovered_from": "discovered",
    "parent": "children",
    "superseded_by": "replaces",
    "duplicate_of": "duplicates",
}
