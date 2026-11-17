"""The MCP tools that read the backlog by who has to act."""

from __future__ import annotations

from tadu.mcp_property import mcp_property
from tadu.mcp_tool import mcp_tool

PERSON = mcp_property("string", "person id to act for; default: `me` of the workspace, else anyone")
JSON = mcp_property("boolean", "one JSON object per item instead of text lines")

MCP_ATTENTION_TOOLS = (
    mcp_tool(
        "next",
        "Tasks you can do now without a person, most pressing first. Use it when the user "
        "asks you to work alone or will be away (AFK). It leaves out decisions, waiting and "
        "later items, blocked tasks, items whose Not before day is ahead and tasks assigned "
        "only to someone else. Items without a kind are included as work.",
        {"person": PERSON, "json": JSON},
    ),
    mcp_tool(
        "inbox",
        "What waits on a person: decisions to make, follow-ups and checks whose date has "
        "come, and their blocked tasks. Use it when the user is present or asks what is "
        "waiting for them.",
        {"person": PERSON, "json": JSON},
    ),
    mcp_tool(
        "urgent",
        "Urgent or high priority items and items due soon or overdue, grouped by who acts "
        "(do, decide, chase, check, blocked). Use it when the user asks what is urgent.",
        {
            "days": mcp_property("integer", "a date within this many days is due soon; default 1"),
            "json": JSON,
        },
    ),
)
