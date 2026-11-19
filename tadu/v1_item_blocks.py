"""Split a tadu v1 Markdown backlog into its top-level items."""

from __future__ import annotations

from tadu.v1_layout import v1_layout


def v1_item_blocks(lines: list[str]) -> tuple[tuple[tuple[str, ...], str | None], ...]:
    """Each unfenced top-level item's lines, with the `##` section it sits in (see v1_layout)."""
    return tuple((block, section) for _, block, section in v1_layout(lines).items)
