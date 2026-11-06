"""Build a saved view from its table row."""

from __future__ import annotations

from tadu.card_filter import CardFilter
from tadu.check_row_keys import check_row_keys
from tadu.columns import COLUMNS
from tadu.optional_choice import optional_choice
from tadu.optional_date import optional_date
from tadu.optional_flag import optional_flag
from tadu.optional_text import optional_text
from tadu.priorities import PRIORITIES
from tadu.required_text import required_text
from tadu.view_entry import ViewEntry
from tadu.view_keys import VIEW_KEYS


def parse_view(row: dict[str, object]) -> ViewEntry:
    """Read the name and the filter criteria; an unknown key is an error."""
    check_row_keys(row, VIEW_KEYS, "view")
    return ViewEntry(
        required_text(row, "view", "name"),
        CardFilter(
            project=optional_text(row, "view", "project"),
            org=optional_text(row, "view", "org"),
            role=optional_text(row, "view", "role"),
            assignee=optional_text(row, "view", "assignee"),
            column=optional_choice(row, "view", "column", COLUMNS),
            priority=optional_choice(row, "view", "priority", PRIORITIES),
            label=optional_text(row, "view", "label"),
            due_before=optional_date(row, "view", "due_before"),
            include_cancelled=optional_flag(row, "view", "include_cancelled"),
        ),
    )
