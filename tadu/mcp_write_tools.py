"""The MCP tools that change a backlog."""

from __future__ import annotations

from tadu.kinds import KINDS
from tadu.mark_states import MARK_STATES
from tadu.mcp_property import mcp_property
from tadu.mcp_tool import mcp_tool
from tadu.priorities import PRIORITIES
from tadu.queues import QUEUES

REPOSITORY = mcp_property(
    "string",
    "the repository as items show it, or its full path; needed when the server reads more "
    "than one. Folders that share a name show as their full path.",
)

MCP_WRITE_TOOLS = (
    mcp_tool(
        "add",
        "Add one open item to TODO.md. When you meet a question only a person can answer, "
        "add it with kind `decision`, the options and their trade-offs as notes, then go on "
        "with other work instead of waiting or guessing.",
        {
            "title": mcp_property("string", "the item's first line"),
            "category": mcp_property("string", "the ## section to put it under"),
            "kind": mcp_property(
                "string", "task, decision, waiting or later; leave out when unclear", KINDS
            ),
            "priority": mcp_property("string", "item priority", PRIORITIES),
            "assignees": mcp_property("array", "person ids"),
            "due": mcp_property("string", "YYYY-MM-DD: the deadline"),
            "check_on": mcp_property("string", "YYYY-MM-DD: when to look again or follow up"),
            "not_before": mcp_property("string", "YYYY-MM-DD: it cannot start before this day"),
            "labels": mcp_property("array", "labels"),
            "queue": mcp_property("string", "backlog or ready", QUEUES),
            "estimate": mcp_property("integer", "minutes"),
            "notes": mcp_property("array", "paragraphs under the title, one line each"),
            "repository": REPOSITORY,
        },
        ("title",),
        read_only=False,
    ),
    mcp_tool(
        "mark",
        "Set one open item's state: `blocked` with a note naming the blocker (such as the "
        "decision you added), `open` once it is unblocked, or `in_progress`. Also sets or "
        "changes its fields, such as kind or priority, without editing TODO.md.",
        {
            "match": mcp_property("string", "text found in the item's first line"),
            "state": mcp_property("string", "the new state", tuple(MARK_STATES)),
            "kind": mcp_property("string", "set Kind: task, decision, waiting or later", KINDS),
            "priority": mcp_property("string", "set Priority:", PRIORITIES),
            "assignees": mcp_property("array", "set Assignees: person ids"),
            "due": mcp_property("string", "set Due: YYYY-MM-DD"),
            "check_on": mcp_property("string", "set Check on: YYYY-MM-DD"),
            "not_before": mcp_property("string", "set Not before: YYYY-MM-DD"),
            "labels": mcp_property("array", "set Labels:"),
            "queue": mcp_property("string", "set Queue: backlog or ready", QUEUES),
            "estimate": mcp_property("integer", "set Estimate: minutes"),
            "note": mcp_property("string", "a paragraph added to the item; required for blocked"),
            "repository": REPOSITORY,
        },
        ("match",),
        read_only=False,
    ),
    mcp_tool(
        "close",
        "Move one finished open item from TODO.md to TODO_LOG.md. Give `evidence` (a test, "
        "command result, commit or PR) for verified work, or `resolution` for dropped work.",
        {
            "match": mcp_property("string", "text found in the item's first line"),
            "evidence": mcp_property("string", "what proves it is done; logs it as [x]"),
            "resolution": mcp_property("string", "why it no longer applies; logs it as [-]"),
            "result": mcp_property("string", "what changed"),
            "repository": REPOSITORY,
        },
        ("match",),
        read_only=False,
    ),
)
