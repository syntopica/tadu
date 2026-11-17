"""The MCP tools that list and show items."""

from __future__ import annotations

from tadu.columns import COLUMNS
from tadu.kind_filters import KIND_FILTERS
from tadu.mcp_property import mcp_property
from tadu.mcp_tool import mcp_tool
from tadu.priorities import PRIORITIES

MCP_LIST_TOOLS = (
    mcp_tool(
        "list",
        "Items of the backlog as `repository:path:line [column] priority kind title` lines, "
        "filtered. Closed items of the last 14 days are included unless `open` is true.",
        {
            "kind": mcp_property(
                "string", "task, decision, waiting, later, or unclassified", KIND_FILTERS
            ),
            "priority": mcp_property("string", "item priority", PRIORITIES),
            "column": mcp_property("string", "board column", COLUMNS),
            "assignee": mcp_property("string", "person id"),
            "label": mcp_property("string", "item label"),
            "due_before": mcp_property("string", "YYYY-MM-DD; items due before it"),
            "check_before": mcp_property("string", "YYYY-MM-DD; items to check before it"),
            "open": mcp_property("boolean", "only open items"),
            "json": mcp_property("boolean", "one JSON object per item, with its key"),
        },
    ),
    mcp_tool(
        "show",
        "The full text of one item by its key (its ID:, or the k- key `list` gives with json).",
        {"key": mcp_property("string", "the item key")},
        ("key",),
    ),
)
