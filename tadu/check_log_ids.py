"""Checks for an ID both open in TODO.md and closed in TODO_LOG.md, or closed twice."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding
from tadu.id_line_offset import id_line_offset
from tadu.read_open_items import read_open_items
from tadu.read_text_exact import read_text_exact
from tadu.scan_items import scan_items
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path


def check_log_ids(root: Path) -> tuple[Finding, ...]:
    """T005 for an open item whose ID a log entry closed, L007 for an ID closed twice.

    `tadu close` writes the log entry first and removes the item second, so a close that
    stops in between leaves the item in both files (T005); running it again finishes it, but
    an older tadu logged the item a second time (L007). Items without an `ID:` cannot be
    matched and are not checked; a missing or unreadable file is for the other checks to report.
    """
    todo, log = root / "TODO.md", root / "TODO_LOG.md"
    if not log.is_file():
        return ()
    try:
        closed = scan_items(
            read_text_exact(log).splitlines(),
            "",
            "TODO_LOG.md",
            lambda match: match.group(1) in "x-",
        )
        opened = read_open_items(root, ".", "") if todo.is_file() else ()
    except UnreadableFileError:
        return ()
    first_line: dict[str, int] = {}
    repeats: list[Finding] = []
    for entry in closed:
        uid = entry.fields.id
        if uid is None:
            continue
        if uid not in first_line:
            # keys: set only when the ID is not there yet; a repeat is reported as L007.
            first_line[uid] = entry.line
            continue
        line = entry.line + id_line_offset(entry.text, uid)
        message = (
            f"ID {uid} is also closed at line {first_line[uid]}; two entries close one item "
            "(an older tadu logged a stopped close run again twice): keep one"
        )
        repeats.append(Finding("L007", "warning", str(log), line, message))
    findings = [
        Finding(
            "T005",
            "error",
            str(todo),
            item.line + id_line_offset(item.text, item.fields.id),
            f"ID {item.fields.id} is already closed in TODO_LOG.md at line "
            f"{first_line[item.fields.id]}; a close that stopped halfway leaves the item in "
            "both files: run the same tadu close again to finish it (a reopened item needs "
            "a new ID)",
        )
        for item in opened
        if item.fields.id is not None and item.fields.id in first_line
    ]
    return (*findings, *repeats)
