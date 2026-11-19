"""How many lines of each field a change added and removed, as `tadu changes` sums them up."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.history_line import HistoryLine


def line_facts(lines: list[HistoryLine]) -> list[str]:
    """`notes: 1 added, 1 removed` per field, in the order the fields first appear.

    A task's lines carry their field (`notes`, `done_when`...); a TODO.md item's, `text`.
    """
    counts: dict[str, dict[str, int]] = {}
    for line in lines:
        counts.setdefault(line["field"], {"+": 0, "-": 0})[line["op"]] += 1
    facts = []
    for field, count in counts.items():
        parts = [
            f"{count[op]} {word}" for op, word in (("+", "added"), ("-", "removed")) if count[op]
        ]
        facts.append(f"{field}: {', '.join(parts)}")
    return facts
