"""The operations that look up similar items, recent closings and problems."""

from __future__ import annotations

from tadu.operation import Operation
from tadu.param import Param
from tadu.shared_params import DONE_DAYS

LOOKUP_OPERATIONS = (
    Operation(
        "similar",
        "print the items most like a text: check before adding one",
        (
            Param(
                "text",
                "text",
                "the title of the item you are about to add",
                required=True,
                positional=True,
            ),
            Param("limit", "count", "items to print (default 5)", default=5),
            Param("open", "flag", "only open items"),
            Param("json", "flag", "one JSON object per item, with its `overlap` (0 to 1)"),
        ),
    ),
    Operation("feed", "print recently closed items as JSON, newest first", (DONE_DAYS,)),
    Operation(
        "doctor",
        "check repositories against the tadu spec; with --workspace, each of its repositories and "
        "its items as a whole",
        (Param("json", "flag", "one JSON object per finding"),),
    ),
)
