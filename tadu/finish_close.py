"""Finish, in memory, a close that logged its entry and stopped before removing the item."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.fenced_lines import fenced_lines
from tadu.item_category import item_category
from tadu.item_span_end import item_span_end
from tadu.log_entry_conflict import log_entry_conflict
from tadu.markdown_headings import markdown_headings
from tadu.remove_lines import remove_lines
from tadu.render_log_entry import render_log_entry

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem
    from tadu.closing import Closing

PROOF_PREFIXES = ("  - Evidence: ", "  - Resolution: ")
AGAIN = "  - Close run again: "
TAIL_PREFIXES = (*PROOF_PREFIXES, AGAIN)


def finish_close(
    lines: tuple[list[str], list[str]], first: int, entry: BacklogItem, closing: Closing
) -> tuple[list[str], list[str]] | str:
    """The backlog without the item and the log with `entry` completed, or why it cannot be.

    `lines` are those of TODO.md and TODO_LOG.md; the item starts at index `first`.

    The entry already written is the record: its date, title and category stay, and nothing
    is logged twice. What the close run again would add and the entry lacks is kept: new
    evidence goes after the entry's last line, and a result the entry has none of, or text
    the item gained since, goes before its proof line. A different state, result or
    resolution is refused, so nothing recorded is replaced. A close run on another day than
    the entry's adds that day (`Close run again:`), as the entry keeps its own: the day a
    stopped close was finished, or an item reopened under its old ID was closed again.
    """
    todo, log = lines
    end = item_span_end(todo, first)
    section = item_category(markdown_headings(todo, fenced_lines(todo)), first, 2)
    wanted = render_log_entry(todo[first:end], closing, section)[1:]
    if entry.day is not None and entry.day != closing.day:
        wanted.append(f"{AGAIN}{closing.day.isoformat()}")
    recorded = log[entry.line : entry.end_line]
    conflict = log_entry_conflict(entry, recorded, wanted, closing.state)
    if conflict is not None:
        return conflict
    missing = [line for line in wanted if line.strip() and line not in recorded]
    proofs = [line for line in missing if line.startswith(TAIL_PREFIXES)]
    others = [line for line in missing if not line.startswith(TAIL_PREFIXES)]
    offsets = [index for index, line in enumerate(recorded) if line.startswith(PROOF_PREFIXES)]
    at = entry.line + offsets[0] if offsets else entry.end_line
    stop = entry.end_line
    finished = [*log[:at], *others, *log[at:stop], *proofs, *log[stop:]]
    return remove_lines(todo, first, end), finished
