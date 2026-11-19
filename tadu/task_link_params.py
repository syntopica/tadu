"""The arguments of `add` after its fields: relations, notes, criteria and links."""

from __future__ import annotations

from tadu.param import Param

TASK_LINK_PARAMS = (
    Param("parent", "text", "task id or unique prefix of the epic or parent task", format=2),
    Param(
        "discovered_from",
        "text",
        "task id or unique prefix whose work revealed this one",
        format=2,
    ),
    Param("created_by", "text", "person id or agent:<name> (default: $TADU_ACTOR)", format=2),
    Param(
        "blocked_by",
        "list",
        "task id or unique prefix that must close first; repeat for more",
        metavar="TASK",
    ),
    Param(
        "related",
        "list",
        "task id or unique prefix on the same subject; repeat",
        metavar="TASK",
        format=2,
    ),
    Param(
        "note",
        "list",
        'one Markdown line of the notes ("" is a blank line); repeat',
        aliases=("notes",),
        metavar="LINE",
    ),
    Param("done_when", "list", "one acceptance criterion; repeat for more"),
    Param(
        "link",
        "list",
        "URL of a PR, issue or document; repeat for more",
        aliases=("links",),
        format=2,
    ),
)
