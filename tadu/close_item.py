"""Move one backlog item into the log, in memory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.fenced_lines import fenced_lines
from tadu.insert_block import insert_block
from tadu.item_category import item_category
from tadu.item_span_end import item_span_end
from tadu.log_is_newest_first import log_is_newest_first
from tadu.log_view import LogView
from tadu.markdown_headings import markdown_headings
from tadu.place_log_entry import place_log_entry
from tadu.remove_lines import remove_lines
from tadu.render_log_entry import render_log_entry

if TYPE_CHECKING:
    from tadu.closing import Closing


def close_item(
    todo: list[str], log: list[str], first: int, closing: Closing
) -> tuple[list[str], list[str]]:
    """The backlog without the item at `first` and the log with its entry in place."""
    end = item_span_end(todo, first)
    section = item_category(markdown_headings(todo, fenced_lines(todo)), first, 2)
    entry = render_log_entry(todo[first:end], closing, section)
    fenced = fenced_lines(log)
    view = LogView(log, fenced, markdown_headings(log, fenced))
    newest_first = log_is_newest_first(log, fenced)
    index, headings = place_log_entry(view, closing.day, newest_first=newest_first)
    return remove_lines(todo, first, end), insert_block(log, index, headings + entry)
