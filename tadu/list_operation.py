"""The list operation."""

from __future__ import annotations

from tadu.columns import COLUMNS
from tadu.kind_filters import KIND_FILTERS
from tadu.operation import Operation
from tadu.param import Param
from tadu.priorities import PRIORITIES
from tadu.shared_params import DONE_DAYS, JSON_ITEMS, PAGE

LIST_OPERATION = Operation(
    "list",
    "print backlog items as lines or JSON",
    (
        DONE_DAYS,
        Param("view", "text", "saved view of the workspace; flags given beside it win"),
        JSON_ITEMS,
        Param("compact", "flag", "with --json, omit raw task text; use show for details"),
        Param("project", "text", "project id"),
        Param("org", "text", "organization id"),
        Param("role", "text", "organization role"),
        Param("assignee", "text", "person id"),
        Param("column", "choice", "board column", COLUMNS),
        Param("priority", "choice", "item priority", PRIORITIES),
        Param("kind", "choice", "item kind; unclassified for items without one", KIND_FILTERS),
        Param("label", "text", "item label"),
        Param("due_before", "day", "items due before this day"),
        Param("check_before", "day", "Check on: date before this day"),
        Param("include_cancelled", "flag", "keep cancelled items"),
        Param("category", "text", "categories, comma-separated (any of)"),
        Param("type", "text", "task types, comma-separated (any of)"),
        Param("milestone", "text", "milestone slug"),
        Param("text", "text", "case-insensitive regular expression over title and text"),
        Param("due_within", "count", "due within N days, overdue included", metavar="DAYS"),
        Param("overdue", "flag", "due before today"),
        Param("min_priority", "choice", "this priority or more urgent", PRIORITIES),
        Param("history", "flag", "closed items of all time, not --done-days", exclusive="closed"),
        Param(
            "open",
            "flag",
            "open items only, not --done-days; faster, closed tasks are not read",
            exclusive="closed",
        ),
        Param(
            "sort",
            "choice",
            "order (default: file)",
            ("file", "priority", "due", "closed"),
            default="file",
        ),
        *PAGE,
    ),
    describe="Items of the backlog as `repository:path:line [column] priority kind title` lines, "
    "filtered. Closed items of the last 14 days (`done_days`) are included unless `open` is "
    "true; `history` includes every closed item.",
)
