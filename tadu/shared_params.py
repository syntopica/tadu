"""Arguments several operations share."""

from __future__ import annotations

from tadu.param import Param

DONE_DAYS = Param(
    "done_days",
    "count",
    "show done and cancelled items this many days back (default: 14)",
    default=14,
)
JSON_ITEMS = Param("json", "switch", "one JSON object per item")
PAGE = (
    Param("limit", "count", "items to print (default 100; 0 = all)", default=100),
    Param("offset", "count", "items to skip", default=0),
)
FIELD = Param(
    "field",
    "list",
    "only changes of this field, such as state or assignee; repeat or comma-separate",
    default=[],
    metavar="NAME",
    aliases=("fields",),
)
AUTHOR = Param("author", "text", "commits whose author name contains it", metavar="TEXT")
PERSON = Param(
    "person", "text", "person id to act for (default: `me` of the workspace, else anyone)"
)
ITEM_ID = Param(
    "id",
    "text",
    "the item's ID, a unique prefix of a task id (10 characters or more), or the k- key "
    "`list --json` gives",
    exclusive="item",
    required=True,
    aliases=("key",),
)
ITEM_MATCH = Param(
    "match", "text", "text found in the item's first line (a task's title)", exclusive="item"
)
