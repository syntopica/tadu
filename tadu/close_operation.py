"""The close operation, for both backlog formats."""

from __future__ import annotations

from tadu.operation import Operation
from tadu.param import Param
from tadu.shared_params import ITEM_ID, ITEM_MATCH

CLOSE_OPERATION = Operation(
    "close",
    "close one open item: into TODO_LOG.md, or (format 2) into todo/closed/",
    (
        ITEM_ID,
        ITEM_MATCH,
        Param(
            "evidence",
            "text",
            "log it as [x] with this Evidence: line",
            exclusive="proof",
            required=True,
        ),
        Param("resolution", "text", "log it as [-] with this Resolution: line", exclusive="proof"),
        Param(
            "duplicate_of",
            "text",
            "cancel it as a duplicate of this task",
            exclusive="proof",
            format=2,
        ),
        Param("result", "text", "Result: line of the entry"),
        Param("category", "text", "category (default: its ## section)", format=1),
        Param("title", "text", "entry text (default: the item's)", format=1),
        Param("date", "day", "the closing day (default: today)"),
    ),
    access="write",
    describe="Close one finished open item: into TODO_LOG.md, or a task into todo/closed/. "
    "Give `evidence` (a test, command result, commit or PR) for verified work, `resolution` "
    "for dropped work, or `duplicate_of` for a task another one repeats.",
)
