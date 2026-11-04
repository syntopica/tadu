"""Build a person entry from its table row."""

from __future__ import annotations

from tadu.optional_text import optional_text
from tadu.person_entry import PersonEntry
from tadu.required_text import required_text


def parse_person(row: dict[str, object]) -> PersonEntry:
    """Read id, name and the optional organization."""
    return PersonEntry(
        required_text(row, "person", "id"),
        required_text(row, "person", "name"),
        optional_text(row, "person", "organization"),
    )
