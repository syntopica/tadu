"""A saved view as the board lists it."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.view_entry import ViewEntry


def view_summary(view: ViewEntry) -> dict[str, str]:
    """The name and the criteria that are set, as `key=value` text in filter order."""
    criteria = [f"{key}={value}" for key, value in asdict(view.card_filter).items() if value]
    return {"name": view.name, "criteria": ", ".join(criteria)}
