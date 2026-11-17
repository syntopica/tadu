"""The lines of a new top-level backlog item."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.category_prefix_pattern import CATEGORY_PREFIX_PATTERN

if TYPE_CHECKING:
    from tadu.add_request import AddRequest


def item_lines(request: AddRequest) -> list[str]:
    """`- [ ] **Category:** Title`, then each field and note as its own indented paragraph."""
    title = request.title.strip()
    if request.category is not None and not CATEGORY_PREFIX_PATTERN.match(title):
        title = f"**{request.category.strip()}:** {title}"
    lines = [f"- [ ] {title}"]
    for name, value in request.fields:
        lines += ["", f"  {name}: {value.strip()}"]
    for note in request.notes:
        lines += ["", f"  {note.strip()}"]
    return lines
