"""The parts of a tadu v1 item's continuation lines."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class V1ItemParts:
    """Fields, log bullets (Result, Evidence, Resolution, Files), notes, done-when and blockers.

    notes and done_when are Markdown lines, dedented by the item's two spaces, with "" between
    paragraphs.
    """

    fields: dict[str, str] = field(default_factory=dict)
    bullets: dict[str, list[str]] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    done_when: list[str] = field(default_factory=list)
    blocked_by: list[str] = field(default_factory=list)
