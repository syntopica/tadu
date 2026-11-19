"""The argparse keyword arguments an operation argument's kind implies."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from tadu.non_negative_int import non_negative_int
from tadu.param_help import param_help

if TYPE_CHECKING:
    from tadu.param import Param

TYPES = {"day": date.fromisoformat, "count": non_negative_int}


def param_options(param: Param) -> dict[str, object]:
    """Help, and the action, type, choices, metavar and default the argument has.

    A flag stores true; an option list appends; a day parses as a date (shown as YYYY-MM-DD)
    and a count as a whole number of zero or more, unless `parse` says otherwise.
    """
    options: dict[str, object] = {"help": param_help(param)}
    if param.kind == "flag":
        options["action"] = "store_true"
    elif param.kind == "list" and not param.positional:
        options["action"] = "append"
    if param.parse is not None or param.kind in TYPES:
        options["type"] = param.parse or TYPES[param.kind]
    if param.choices:
        options["choices"] = param.choices
    metavar = param.metavar or ("YYYY-MM-DD" if param.kind == "day" else None)
    if metavar:
        options["metavar"] = metavar
    if param.default is not None:
        options["default"] = param.default
    return options
