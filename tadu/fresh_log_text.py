"""The closed-work log tadu init writes into a repository that has none."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date


def fresh_log_text(today: date) -> str:
    """Return a TODO_LOG.md whose log marker dates adoption to `today`."""
    return (
        "# TODO Log\n"
        "\n"
        "> Searchable record of closed project work. Active work lives in `TODO.md`.\n"
        "\n"
        f"<!-- tadu:log v1 since {today.isoformat()} -->\n"
    )
